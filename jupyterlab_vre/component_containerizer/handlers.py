import copy
import datetime
import hashlib
import importlib
import json
import logging
import os
import re
import sys
import traceback
import uuid
from builtins import Exception
from pathlib import Path
from time import sleep

import autopep8
import distro
import jsonschema
import nbformat as nb
import requests
from github import Github
from github.GithubException import UnknownObjectException
from jinja2 import Environment, PackageLoader
from notebook.base.handlers import APIHandler
from slugify import slugify
from tornado import web

from jupyterlab_vre.database.catalog import Catalog
from jupyterlab_vre.database.cell import Cell
from jupyterlab_vre.services.containerizer.Rcontainerizer import Rcontainerizer
from jupyterlab_vre.services.converter.converter import ConverterReactFlowChart
from jupyterlab_vre.services.extractor.extractor import DummyExtractor
from jupyterlab_vre.services.extractor.pyextractor import PyExtractor
from jupyterlab_vre.services.extractor.rextractor import RExtractor
from jupyterlab_vre.services.extractor.headerextractor import HeaderExtractor

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


def query_registry_for_image(image_repo, image_name):
    m = re.match(r'^docker.io/(\w+)', image_name)
    if m:
        # Docker Hub
        url = f'https://hub.docker.com/v2/repositories/{m.group(1)}/{image_name}'
        headers = {}
    else:
        # OCI registries
        domain = image_repo.split('/')[0]
        path = '/'.join(image_repo.split('/')[1:])
        url = f'https://{domain}/v2/{path}/{image_name}/tags/list'
        # OCI registries require authentication, even for public registries.
        # The token should be set in the $OCI_TOKEN environment variable.
        # For ghcr.io, connections still succeed when $OCI_TOKEN is unset (this
        # results in header "Authorization: Bearer None", which grants access
        # to public registries, although it is not officially documented). If
        # this fails, or when accessing private registries, OCI_TOKEN should be
        # a base64-encoded GitHub classic access token with the read:packages
        # scope.
        headers = {
            "Authorization": f"Bearer {os.getenv('OCI_TOKEN')}",
            }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return None


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

        source = notebook.cells[cell_index].source

        if notebook.cells[cell_index].cell_type != 'code':
            # dummy extractor for non-code cells (e.g. markdown)
            extractor = DummyExtractor(notebook, source)
        else:
            # extractor based on the cell header
            try:
                extractor = HeaderExtractor(notebook, source)
            except jsonschema.ValidationError as e:
                self.set_status(400, f"Invalid cell header")
                self.write(
                    {
                        'message': f"Error in cell header: {e}",
                        'reason': None,
                        'traceback': traceback.format_exception(e),
                    }
                )
                self.flush()
                return

            # Extractor based on code analysis. Used if the cell has no header,
            # or if some values are not specified in the header
            if not extractor.is_complete():
                if kernel == "IRkernel":
                    code_extractor = RExtractor(notebook, source)
                else:
                    code_extractor = PyExtractor(notebook, source)
                extractor.add_missing_values(code_extractor)

        extracted_nb = extract_cell_by_index(notebook, cell_index)
        if kernel == "IRkernel":
            extracted_nb = set_notebook_kernel(extracted_nb, 'R')
        else:
            extracted_nb = set_notebook_kernel(extracted_nb, 'python3')

        # initialize variables
        title = source.partition('\n')[0].strip()
        title = slugify(title) if title and title[0] == "#" else "Untitled"

        if 'JUPYTERHUB_USER' in os.environ:
            title += '-' + slugify(os.environ['JUPYTERHUB_USER'])

        # If any of these change, we create a new cell in the catalog.
        # This matches the cell properties saved in workflows.
        cell_identity_dict = {
            'title': title,
            'params': extractor.params,
            'inputs': extractor.ins,
            'outputs': extractor.outs,
            }
        cell_identity_str = json.dumps(cell_identity_dict, sort_keys=True)
        node_id = hashlib.sha1(cell_identity_str.encode()).hexdigest()[:7]

        cell = Cell(
            node_id=node_id,
            title=title,
            task_name=slugify(title.lower()),
            original_source=source,
            inputs=extractor.ins,
            outputs=extractor.outs,
            params={},
            confs=extractor.confs,
            dependencies=extractor.dependencies,
            container_source="",
            kernel=kernel,
            notebook_dict=extracted_nb.dict()
        )
        cell.integrate_configuration()
        extractor.params = extractor.extract_cell_params(cell.original_source)
        cell.add_params(extractor.params)
        cell.add_param_values(extractor.params)

        node = ConverterReactFlowChart.get_node(
            node_id,
            title,
            set(extractor.ins),
            set(extractor.outs),
            extractor.params,
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


class BaseImageTagsHandler(APIHandler):
    logger = logging.getLogger(__name__)

    @web.authenticated
    async def get(self):
        url = os.getenv(
            'BASE_IMAGE_TAGS_URL',
            'https://github.com/QCDIS/NaaVRE-flavors/releases/latest/download/base_image_tags.json',
            )
        logger.debug(f'Base image tags URL: {url}')
        print(f'Base image tags URL: {url}')
        try:
            res = requests.get(url)
            res.raise_for_status()
            dat = res.json()
        except (
                requests.ConnectionError,
                requests.HTTPError,
                requests.JSONDecodeError,
                ) as e:
            msg = f'Error loading base image tags from {url}\n{e}'
            logger.debug(msg)
            print(msg)
            self.set_status(500)
            self.write(msg)
            return
        return self.write(dat)


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
                job['head_sha'] = run['head_sha']
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
            doc_cell = Catalog.get_cell_from_og_node_id(current_cell.node_id)
            if doc_cell:
                Catalog.update_cell(current_cell)
            else:
                Catalog.add_cell(current_cell)
        except Exception as ex:
            logger.error('Error adding or updating cell in catalog: ' + str(ex))
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
        image_repo = registry_credentials[0]['url']
        if not image_repo:
            self.set_status(400)
            self.write_error('Registry not found')
            logger.error('Registry not found')
            self.flush()
            return

        if current_cell.kernel == "IRkernel":
            files_info = Rcontainerizer.get_files_info(cell=current_cell, cells_path=cells_path)
            Rcontainerizer.build_templates(
                cell=current_cell,
                files_info=files_info,
                module_name_mapping=load_module_name_mapping(),
                )
        elif 'python' in current_cell.kernel.lower():
            files_info = get_files_info(cell=current_cell)
            build_templates(
                cell=current_cell,
                files_info=files_info,
                module_name_mapping=load_module_name_mapping(),
                )
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
        do_dispatch_github_workflow, image_version = create_or_update_cell_in_repository(
            task_name=current_cell.task_name,
            repository=gh_repository,
            files_info=files_info,
            )
        if not image_version:
            raise Exception('Error! image_version not set')
        wf_id = str(uuid.uuid4())

        if os.getenv('DEBUG') and os.getenv('DEBUG').lower() == 'true':
            do_dispatch_github_workflow = True
        else:
            image_info = query_registry_for_image(
                image_repo=image_repo,
                image_name=current_cell.task_name,
                )
            if not image_info:
                do_dispatch_github_workflow = True

        image_version = image_version[:7]
        if do_dispatch_github_workflow:
            resp = dispatch_github_workflow(
                owner,
                repository_name,
                current_cell.task_name,
                files_info,
                repo_token,
                image_repo,
                wf_id=wf_id,
                image_version=image_version
            )
            if resp.status_code != 201 and resp.status_code != 200 and resp.status_code != 204:
                self.set_status(400)
                self.write(resp.text)
                logger.error(resp.text)
                self.flush()
                return
            current_cell.set_image_version(image_version)
            Catalog.delete_cell_from_task_name(current_cell.task_name)
            Catalog.add_cell(current_cell)

        print(json.dumps({'wf_id': wf_id, 'dispatched_github_workflow': do_dispatch_github_workflow, 'image_version': image_version}, indent=4))
        self.write(json.dumps({'wf_id': wf_id, 'dispatched_github_workflow': do_dispatch_github_workflow, 'image_version': image_version}))
        self.flush()


def create_or_update_cell_in_repository(task_name, repository, files_info):
    files_updated = False
    code_content_hash = None
    for f_type, f_info in files_info.items():
        f_name = f_info['file_name']
        f_path = f_info['path']
        with open(f_path, 'rb') as f:
            local_content = f.read()
            local_hash = git_hash(local_content)
            try:
                remote_hash = repository.get_contents(path=task_name + '/' + f_name).sha
            except UnknownObjectException:
                remote_hash = None
            logger.debug(f'local_hash: {local_hash}; remote_hash: {remote_hash}')
            if remote_hash is None:
                repository.create_file(
                    path=task_name + '/' + f_name,
                    message=task_name + ' creation',
                    content=local_content,
                    )
            elif remote_hash != local_hash:
                repository.update_file(
                    path=task_name + '/' + f_name,
                    message=task_name + ' update',
                    content=local_content,
                    sha=remote_hash,
                    )
                files_updated = True
            if f_type == 'cell':
                code_content_hash = local_hash
    if not code_content_hash:
        logger.warning('code_content_hash not set')
    return files_updated, code_content_hash


def dispatch_github_workflow(owner, repository_name, task_name, files_info, repository_token, image, wf_id=None, image_version=None):
    url = github_url_repos + '/' + owner + '/' + repository_name + '/actions/workflows/' + github_workflow_file_name + '/dispatches'
    resp = requests.post(
        url=url,
        json={
            'ref': 'refs/heads/main',
            'inputs': {
                'build_dir': task_name,
                'dockerfile': files_info['dockerfile']['file_name'],
                'image_repo': image,
                'image_tag': task_name,
                'id': wf_id,
                'image_version': image_version,
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


def load_module_name_mapping():
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


def map_dependencies(dependencies=None, module_name_mapping=None):
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
            if module_name is None:
                continue
            if not is_standard_module(module_name):
                if conda_package:
                    set_conda_deps.add(module_name)
                if pip_package:
                    set_pip_deps.add(module_name)
    return set_conda_deps, set_pip_deps


def build_templates(cell=None, files_info=None, module_name_mapping=None):
    logger.debug('files_info: ' + str(files_info))
    logger.debug('cell.dependencies: ' + str(cell.dependencies))
    set_conda_deps, set_pip_deps = map_dependencies(
        dependencies=cell.dependencies,
        module_name_mapping=module_name_mapping,
        )
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


def get_files_info(cell=None):
    if not os.path.exists(cells_path):
        os.mkdir(cells_path)
    cell_path = os.path.join(cells_path, cell.task_name)

    cell_file_name = 'task.py'
    dockerfile_name = 'Dockerfile'
    environment_file_name = 'environment.yaml'

    notebook_file_name = None
    if 'visualize-' in cell.task_name:
        notebook_file_name = 'task.ipynb'
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
    info = {
        'cell': {
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