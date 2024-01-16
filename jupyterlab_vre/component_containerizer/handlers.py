import copy
import datetime
import hashlib
import importlib
import json
import logging
import os
from nbformat import read, write, v4 as nbf
import sys
import uuid
from builtins import Exception
from pathlib import Path
from time import sleep

import autopep8
import distro
import nbformat as nb
import requests
from github import Github
from github.GithubException import UnknownObjectException
from jinja2 import Environment, PackageLoader
from notebook.base.handlers import APIHandler
from tornado import web

from jupyterlab_vre.database.catalog import Catalog
from jupyterlab_vre.database.cell import Cell
from jupyterlab_vre.services.containerizer.Rcontainerizer import Rcontainerizer
from jupyterlab_vre.services.converter.converter import ConverterReactFlowChart
from jupyterlab_vre.services.extractor.pyextractor import PyExtractor
from jupyterlab_vre.services.extractor.rextractor import RExtractor

logger = logging.getLogger(__name__)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

# Create a formatter for the log messages
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add the formatter to the handler
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

github_url_repos = 'https://api.github.com/repos'
github_workflow_file_name = 'build-push-docker.yml'
cells_path = os.path.join(str(Path.home()), 'NaaVRE', 'cells')


# code from https://stackoverflow.com/questions/552659/how-to-assign-a-git-sha1s-to-a-file-without-git
def git_hash(contents):
    s = hashlib.sha1()
    s.update(('blob %u\0' % len(contents)).encode('utf-8'))
    s.update(contents)
    return s.hexdigest()


def extract_cell_by_index(notebook, cell_index):
    new_nb = copy.deepcopy(notebook)
    if cell_index < len(notebook.cells):
        new_nb.cells = [notebook.cells[cell_index]]
        return new_nb


def set_notebook_kernel(notebook, kernel):
    new_nb = copy.deepcopy(notebook)
    # Replace kernel name in the notebook metadata
    new_nb.metadata.kernelspec.name = kernel
    new_nb.metadata.kernelspec.display_name = kernel
    new_nb.metadata.kernelspec.language = kernel
    return new_nb


class ExtractorHandler(APIHandler, Catalog):

    @web.authenticated
    async def get(self):
        msg_json = dict(title="Operation not supported.")
        self.write(msg_json)
        self.flush()

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        logging.getLogger(__name__).debug('ExtractorHandler. payload: ' + json.dumps(payload, indent=4))
        print('ExtractorHandler. payload: ' + json.dumps(payload, indent=4))
        kernel = payload['kernel']
        cell_index = payload['cell_index']
        notebook = nb.reads(json.dumps(payload['notebook']), nb.NO_CONVERT)
        # extractor based on the kernel
        extracted_nb = extract_cell_by_index(notebook, cell_index)
        if kernel == "IRkernel":
            extractor = RExtractor(notebook)
            extracted_nb = set_notebook_kernel(extracted_nb, 'R')
        else:
            extractor = PyExtractor(notebook)
            extracted_nb = set_notebook_kernel(extracted_nb, 'python3')

        # initialize variables
        source = notebook.cells[cell_index].source
        title = source.partition('\n')[0].strip()
        title = title.replace('#', '').replace('.', '-').replace(
            '_', '-').replace('(', '-').replace(')', '-').strip() if title and title[0] == "#" else "Untitled"

        if 'JUPYTERHUB_USER' in os.environ:
            title += '-' + os.environ['JUPYTERHUB_USER'].replace('_', '-').replace('(', '-').replace(')', '-').replace(
                '.', '-').replace('@',
                                  '-at-').strip()

        ins = {}
        outs = {}
        params = {}
        confs = []
        dependencies = []

        # Check if cell is code. If cell is for example markdown we get execution from 'extractor.infer_cell_inputs(
        # source)'
        if notebook.cells[cell_index].cell_type == 'code':
            ins = extractor.infer_cell_inputs(source)
            outs = extractor.infer_cell_outputs(source)

            confs = extractor.extract_cell_conf_ref(source)
            dependencies = extractor.infer_cell_dependencies(source, confs)

        node_id = str(uuid.uuid4())[:7]
        cell = Cell(
            node_id=node_id,
            title=title,
            task_name=title.lower().replace(' ', '-').replace('.', '-'),
            original_source=source,
            inputs=ins,
            outputs=outs,
            params=params,
            confs=confs,
            dependencies=dependencies,
            container_source="",
            kernel=kernel,
            notebook_dict=extracted_nb.dict()
        )
        if notebook.cells[cell_index].cell_type == 'code':
            cell.integrate_configuration()
            params = extractor.extract_cell_params(cell.original_source)
            cell.add_params(params)
            cell.add_param_values(params)

        node = ConverterReactFlowChart.get_node(
            node_id,
            title,
            set(ins),
            set(outs),
            params,
            dependencies
        )

        chart = {
            'offset': {
                'x': 0,
                'y': 0,
            },
            'scale': 1,
            'nodes': {node_id: node},
            'links': {},
            'selected': {},
            'hovered': {},
        }

        cell.chart_obj = chart
        Catalog.editor_buffer = copy.deepcopy(cell)
        self.write(cell.toJSON())
        self.flush()


class TypesHandler(APIHandler, Catalog):
    logger = logging.getLogger(__name__)

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        logger.debug('TypesHandler. payload: ' + str(payload))
        port = payload['port']
        p_type = payload['type']
        cell = Catalog.editor_buffer
        cell.types[port] = p_type


class BaseImageHandler(APIHandler, Catalog):
    logger = logging.getLogger(__name__)

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        logger.debug('BaseImageHandler. payload: ' + str(payload))
        print('BaseImageHandler. payload: ' + str(payload))
        base_image = payload['image']
        cell = Catalog.editor_buffer
        cell.base_image = base_image


def wait_for_github_api_resources():
    github = Github(Catalog.get_repositories()[0]['token'])
    rate_limit = github.get_rate_limit()
    while rate_limit.core.remaining <= 0:
        reset = rate_limit.core.reset
        # Calculate remaining time for reset
        remaining_time = reset.timestamp() - datetime.datetime.now().timestamp()
        logger.debug(f'Remaining time for reset: {remaining_time} s')
        logger.debug(f'API rate exceeded, waiting')
        logger.debug(f'Sleeping for: {remaining_time + 1}')
        sleep(remaining_time + 1)
        rate_limit = github.get_rate_limit()


def find_job(
        wf_id=None,
        wf_creation_utc=None,
        owner=None,
        repository_name=None,
        token=None,
        job_id=None,
        ):
    f""" Find Github workflow job

    If job_id is set, retrieve it through
    https://api.github.com/repos/{owner}/{repository_name}/actions/jobs/{job_id}

    Else, get all workflows runs created around wf_creation_utc through
    https://api.github.com/repos/{owner}/{repository_name}/actions/runs
    and find the one matching {wf_id}
    """
    if job_id:
        jobs_url = github_url_repos + '/' + owner + '/' + repository_name + '/actions/jobs/' + str(job_id)
        wait_for_github_api_resources()
        job = get_github_workflow_jobs(jobs_url, token=token)
        return job
    wait_for_github_api_resources()
    runs = get_github_workflow_runs(
        owner=owner,
        repository_name=repository_name,
        t_utc=wf_creation_utc,
        token=token)
    if not runs:
        return None
    for run in runs['workflow_runs']:
        jobs_url = run['jobs_url']
        wait_for_github_api_resources()
        jobs = get_github_workflow_jobs(jobs_url, token=token)
        for job in jobs['jobs']:
            if job['name'] == wf_id:
                return job
    return None


def wait_for_job(
        wf_id=None,
        wf_creation_utc=None,
        owner=None,
        repository_name=None,
        token=None,
        job_id=None,
        timeout=200,
        wait_for_completion=False,
        ):
    """ Call find_job until something is returned or timeout is reached

    :param wf_id: passed to find_job
    :param wf_creation_utc: passed to find_job
    :param owner: passed to find_job
    :param repository_name: passed to find_job
    :param token: passed to find_job
    :param job_id: passed to find_job
    :param timeout: timeout in seconds
    :param wait_for_completion: wait for the job's status to be 'complete'

    :return: job or None
    """
    start_time = datetime.datetime.now().timestamp()  # seconds
    stop_time = start_time + timeout
    while datetime.datetime.now().timestamp() < stop_time:
        job = find_job(
            wf_id=wf_id,
            wf_creation_utc=wf_creation_utc,
            owner=owner,
            repository_name=repository_name,
            token=token,
            job_id=job_id,
            )
        if job:
            if not wait_for_completion:
                return job
            if wait_for_completion and (job['status'] == 'completed'):
                return job
        sleep(5)


def write_cell_to_file(current_cell):
    Path('/tmp/workflow_cells/cells').mkdir(parents=True, exist_ok=True)
    with open('/tmp/workflow_cells/cells/' + current_cell.task_name + '.json', 'w') as f:
        f.write(current_cell.toJSON())
        f.close()


class CellsHandler(APIHandler, Catalog):
    logger = logging.getLogger(__name__)

    @web.authenticated
    async def get(self):
        msg_json = dict(title='Operation not supported.')
        self.write(msg_json)
        self.flush()

    @web.authenticated
    async def post(self, *args, **kwargs):
        try:
            current_cell = Catalog.editor_buffer
            current_cell.clean_code()
            current_cell.clean_title()
            current_cell.clean_task_name()
        except Exception as ex:
            logger.error('Error setting cell: ' + str(ex))
            self.set_status(400)
            self.write('Error setting cell: ' + str(ex))
            self.write_error('Error setting cell: ' + str(ex))
            self.flush()
            return

        logger.debug('current_cell: ' + current_cell.toJSON())
        all_vars = current_cell.params + current_cell.inputs + current_cell.outputs
        for parm_name in all_vars:
            if parm_name not in current_cell.types:
                logger.error(parm_name + ' has not type')
                self.set_status(400)
                self.write(parm_name + ' has not type')
                self.write_error(parm_name + ' has not type')
                self.flush()
                return

        if not hasattr(current_cell, 'base_image'):
            logger.error(current_cell.task_name +
                         ' has not base image not selected')
            self.set_status(400)
            self.write(current_cell.task_name + ' has not base image selected')
            self.write_error(current_cell.task_name +
                             ' has not base not image selected')
            self.flush()
            return
        try:
            logger.debug('Delete if exists: ' + current_cell.task_name)
            Catalog.delete_cell_from_task_name(current_cell.task_name)
            Catalog.add_cell(current_cell)
        except Exception as ex:
            logger.error('Error adding cell in catalog: ' + str(ex))
            self.set_status(400)
            self.write('Error adding cell catalog: ' + str(ex))
            self.write_error('Error adding cell catalog: ' + str(ex))
            self.flush()
            return

        if os.getenv('DEBUG'):
            write_cell_to_file(current_cell)

        if not os.path.exists(cells_path):
            os.mkdir(cells_path)

        cell_path = os.path.join(cells_path, current_cell.task_name)

        if os.path.exists(cell_path):
            for files in os.listdir(cell_path):
                path = os.path.join(cell_path, files)
                if os.path.isfile(path):
                    os.remove(path)
        else:
            os.mkdir(cell_path)

        registry_credentials = Catalog.get_registry_credentials()
        if not registry_credentials or len(registry_credentials) <= 0:
            self.set_status(400)
            self.write_error('Registry credentials not found')
            logger.error('Registry credentials not found')
            self.flush()
            return
        registry_url = registry_credentials[0]['url']
        if not registry_url:
            self.set_status(400)
            self.write_error('Registry url not found')
            logger.error('Registry url not found')
            self.flush()
            return
        image_repo = registry_url.split(
            'https://hub.docker.com/u/')[1]

        if not image_repo:
            self.set_status(400)
            self.write_error('Registry not found')
            logger.error('Registry not found')
            self.flush()
            return

        if current_cell.kernel == "IRkernel":
            files_info = Rcontainerizer.get_files_info(cell=current_cell, image_repo=image_repo, cells_path=cells_path)
            Rcontainerizer.build_templates(cell=current_cell, files_info=files_info)
        elif 'python' in current_cell.kernel.lower():
            files_info = get_files_info(cell=current_cell, image_repo=image_repo)
            build_templates(cell=current_cell, files_info=files_info)
        else:
            self.set_status(400)
            self.write_error('Kernel: ' + current_cell.kernel + ' not supported')
            logger.error('Kernel: ' + current_cell.kernel + ' not supported')
            self.flush()
            return

        # upload to GIT
        cat_repositories = Catalog.get_repositories()

        repo_token = cat_repositories[0]['token']
        if not repo_token:
            self.set_status(400)
            self.write_error('Repository token not found')
            logger.error('Repository token not found')
            self.flush()
            return

        gh_token = Github(cat_repositories[0]['token'])
        url_repos = cat_repositories[0]['url']
        if not url_repos:
            self.set_status(400)
            self.write_error('Repository url not found')
            logger.error('Repository url not found')
            self.flush()
            return

        owner = url_repos.split('https://github.com/')[1].split('/')[0]
        repository_name = url_repos.split('https://github.com/')[1].split('/')[1]
        if '.git' in repository_name:
            repository_name = repository_name.split('.git')[0]
        try:
            gh_repository = gh_token.get_repo(owner + '/' + repository_name)
        except Exception as ex:
            self.set_status(400)
            self.set_status(400)
            if hasattr(ex, 'message'):
                error_message = 'Error getting repository: ' + str(ex) + ' ' + ex.message
            else:
                error_message = 'Error getting repository: ' + str(ex)
            self.write(error_message)
            logger.error(error_message)
            self.flush()
            return
        files_updated = False
        commit = gh_repository.get_commits(path=current_cell.task_name)
        if commit.totalCount > 0:
            try:
                files_updated = update_cell_in_repository(task_name=current_cell.task_name, repository=gh_repository,
                                                          files_info=files_info)
            except UnknownObjectException as ex:
                create_cell_in_repository(task_name=current_cell.task_name, repository=gh_repository,
                                          files_info=files_info)
                files_updated = True
        elif commit.totalCount <= 0:
            create_cell_in_repository(task_name=current_cell.task_name, repository=gh_repository,
                                      files_info=files_info)
            files_updated = True
        wf_id = str(uuid.uuid4())
        # Here we force to run the containerization workflow since we can't if the docker image is already built. Also,
        # when testing the workflow we need to run it again
        files_updated = True
        if files_updated:
            resp = dispatch_github_workflow(
                owner,
                repository_name,
                current_cell.task_name,
                files_info,
                repo_token,
                image_repo,
                wf_id=wf_id
            )
            if resp.status_code != 201 and resp.status_code != 200 and resp.status_code != 204:
                self.set_status(400)
                self.write(resp.text)
                logger.error(resp.text)
                self.flush()
                return
            # job = find_job(wf_id=wf_id, owner=owner, repository_name=repository_name, token=repo_token)
            # print(job)
        self.write(json.dumps({'wf_id': wf_id, 'files_updated': files_updated}))
        self.flush()


def create_cell_in_repository(task_name=None, repository=None, files_info=None):
    for f_type, f_info in files_info.items():
        f_name = f_info['file_name']
        f_path = f_info['path']
        with open(f_path, 'rb') as f:
            content = f.read()
            repository.create_file(
                path=task_name + '/' + f_name,
                message=task_name + ' creation',
                content=content,
            )


def update_cell_in_repository(task_name=None, repository=None, files_info=None):
    files_updated = False
    for f_type, f_info in files_info.items():
        f_name = f_info['file_name']
        f_path = f_info['path']
        remote_content = repository.get_contents(
            path=task_name + '/' + f_name)
        with open(f_path, 'rb') as f:
            local_content = f.read()
            local_hash = git_hash(local_content)
            remote_hash = remote_content.sha
            logger.debug('local_hash: ' + local_hash + ' remote_hash: ' + remote_hash)
            if remote_hash != local_hash:
                files_updated = True
                repository.update_file(
                    path=task_name + '/' + f_name,
                    message=task_name + ' update',
                    content=local_content,
                    sha=remote_content.sha
                )
        f.close()
    return files_updated


def dispatch_github_workflow(owner, repository_name, task_name, files_info, repository_token, image, wf_id=None):
    resp = requests.post(
        url=github_url_repos + '/' + owner + '/' + repository_name + '/actions/workflows/' + github_workflow_file_name + '/dispatches',
        json={
            'ref': 'refs/heads/main',
            'inputs': {
                'build_dir': task_name,
                'dockerfile': files_info['dockerfile']['file_name'],
                'image_repo': image,
                'image_tag': task_name,
                "id": wf_id
            }
        },
        verify=False,
        headers={'Accept': 'application/vnd.github.v3+json',
                 'Authorization': 'token ' + repository_token}
    )
    return resp


def get_github_workflow_runs(owner=None, repository_name=None, t_utc=None, token=None):
    workflow_runs_url = github_url_repos + '/' + owner + '/' + repository_name + '/actions/runs'
    if t_utc:
        t_start = (t_utc - datetime.timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        t_stop = (t_utc + datetime.timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        workflow_runs_url += f"?created={t_start}..{t_stop}"
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    workflow_runs = requests.get(url=workflow_runs_url, verify=False,
                                 headers=headers)
    if workflow_runs.status_code != 200:
        return None
    workflow_runs_json = json.loads(workflow_runs.text)
    return workflow_runs_json


def get_github_workflow_jobs(jobs_url=None, token=None):
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    jobs = requests.get(url=jobs_url, verify=False,
                        headers=headers)
    if jobs.status_code == 200:
        return json.loads(jobs.text)
    else:
        raise Exception('Error getting jobs for workflow run: ' + jobs.text)


def is_standard_module(module_name):
    if module_name in sys.builtin_module_names:
        return True
    installation_path = None
    try:
        installation_path = importlib.import_module(module_name).__file__
    except ImportError:
        return False
    linux_os = distro.id()
    return 'dist-packages' not in installation_path if linux_os == 'Ubuntu' else 'site-packages' not in installation_path


def load_module_names_mapping():
    module_mapping_url = os.getenv('MODULE_MAPPING_URL')
    module_mapping = {}
    if module_mapping_url:
        resp = requests.get(module_mapping_url)
        module_mapping = json.loads(resp.text)
    module_name_mapping_path = os.path.join(
        str(Path.home()), 'NaaVRE', 'module_name_mapping.json')
    if not os.path.exists(module_name_mapping_path):
        with open(module_name_mapping_path, 'w') as module_name_mapping_file:
            json.dump(module_mapping, module_name_mapping_file, indent=4)
        module_name_mapping_file.close()

    module_name_mapping_file = open(module_name_mapping_path)
    loaded_module_name_mapping = json.load(module_name_mapping_file)
    loaded_module_name_mapping.update(module_mapping)
    module_name_mapping_file.close()
    return loaded_module_name_mapping


def map_dependencies(dependencies=None):
    module_name_mapping = load_module_names_mapping()
    set_conda_deps = set([])
    set_pip_deps = set([])
    for dep in dependencies:
        if 'module' in dep and dep['module']:
            if '.' in dep['module']:
                module_name = dep['module'].split('.')[0]
            else:
                module_name = dep['module']
        elif 'name' in dep and dep['name']:
            module_name = dep['name']
        if module_name:
            conda_package = True
            pip_package = False
            if module_name in module_name_mapping['conda'].keys():
                module_name = module_name_mapping['conda'][module_name]
                pip_package = False
                conda_package = True
            if module_name in module_name_mapping['pip'].keys():
                module_name = module_name_mapping['pip'][module_name]
                pip_package = True
                conda_package = False
            if not is_standard_module(module_name):
                if conda_package:
                    set_conda_deps.add(module_name)
                if pip_package:
                    set_pip_deps.add(module_name)
    return set_conda_deps, set_pip_deps


def build_templates(cell=None, files_info=None):
    logger.debug('files_info: ' + str(files_info))
    logger.debug('cell.dependencies: ' + str(cell.dependencies))
    set_conda_deps, set_pip_deps = map_dependencies(dependencies=cell.dependencies)
    loader = PackageLoader('jupyterlab_vre', 'templates')
    template_env = Environment(
        loader=loader, trim_blocks=True, lstrip_blocks=True)

    if cell.title.startswith('visualize-'):
        template_cell = template_env.get_template('vis_cell_template.jinja2')
        if cell.notebook_dict:
            notebook_path = os.path.join(files_info['cell']['path']).replace('.py', '.ipynb')
            with open(notebook_path, 'w') as f:
                f.write(json.dumps(cell.notebook_dict, indent=4))
                f.close()
    else:
        template_cell = template_env.get_template('py_cell_template.jinja2')
    template_dockerfile = template_env.get_template(
        'dockerfile_template_conda.jinja2')


    compiled_code = template_cell.render(cell=cell, deps=cell.generate_dependencies(), types=cell.types,
                                         confs=cell.generate_configuration_dict())

    compiled_code = autopep8.fix_code(compiled_code)
    cell.container_source = compiled_code

    template_cell.stream(cell=cell, deps=cell.generate_dependencies(), types=cell.types,
                         confs=cell.generate_configuration_dict()).dump(files_info['cell']['path'])
    template_dockerfile.stream(task_name=cell.task_name, base_image=cell.base_image).dump(
        files_info['dockerfile']['path'])

    template_conda = template_env.get_template('conda_env_template.jinja2')
    template_conda.stream(base_image=cell.base_image, conda_deps=list(set_conda_deps),
                          pip_deps=list(set_pip_deps)).dump(files_info['environment']['path'])


def get_files_info(cell=None, image_repo=None):
    if not os.path.exists(cells_path):
        os.mkdir(cells_path)
    cell_path = os.path.join(cells_path, cell.task_name)

    cell_file_name = cell.task_name + '.py'
    dockerfile_name = 'Dockerfile.' + image_repo + '.' + cell.task_name
    environment_file_name = cell.task_name + '-environment.yaml'

    notebook_file_name = None
    if 'visualize-' in cell.task_name:
        notebook_file_name = cell.task_name + '.ipynb'
    if os.path.exists(cell_path):
        for files in os.listdir(cell_path):
            path = os.path.join(cell_path, files)
            if os.path.isfile(path):
                os.remove(path)
    else:
        os.mkdir(cell_path)

    cell_file_path = os.path.join(cell_path, cell_file_name)
    dockerfile_file_path = os.path.join(cell_path, dockerfile_name)
    env_file_path = os.path.join(cell_path, environment_file_name)
    info = {'cell': {
        'file_name': cell_file_name,
        'path': cell_file_path},
        'dockerfile': {
            'file_name': dockerfile_name,
            'path': dockerfile_file_path},
        'environment': {
            'file_name': environment_file_name,
            'path': env_file_path}
    }
    if notebook_file_name:
        info['notebook'] = {
            'file_name': notebook_file_name,
            'path': os.path.join(cell_path, notebook_file_name)
        }
    return info
