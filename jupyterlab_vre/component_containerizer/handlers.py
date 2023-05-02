import copy
import hashlib
import importlib
import json
import logging
import os
import sys
import uuid
from builtins import Exception
import datetime
from pathlib import Path

import autopep8
import distro
import nbformat as nb
import requests
from github import Github
from github.GithubException import UnknownObjectException
from jinja2 import Environment, PackageLoader
from jupyterlab_vre.database.cell import Cell
from jupyterlab_vre.database.database import Catalog
from jupyterlab_vre.services.converter.converter import ConverterReactFlowChart
from jupyterlab_vre.services.extractor.RExtractor import RExtractor
from jupyterlab_vre.services.extractor.extractor import Extractor
from jupyterlab_vre.services.containerizer.Rcontainerizer import Rcontainerizer
from notebook.base.handlers import APIHandler
from tornado import web

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

github_url_repos = 'https://api.github.com/repos'
github_workflow_file_name = 'build-push-docker.yml'
cells_path = os.path.join(str(Path.home()), 'NaaVRE', 'cells')


# code from https://stackoverflow.com/questions/552659/how-to-assign-a-git-sha1s-to-a-file-without-git
def git_hash(contents):
    s = hashlib.sha1()
    s.update(('blob %u\0' % len(contents)).encode('utf-8'))
    s.update(contents)
    return s.hexdigest()


class ExtractorHandler(APIHandler, Catalog):

    @web.authenticated
    async def get(self):
        msg_json = dict(title="Operation not supported.")
        self.write(msg_json)
        self.flush()

    @web.authenticated
    async def post(self, *args, **kwargs):

        # handle request
        payload = self.get_json_body()
        print(json.dumps(payload))
        kernel = payload['kernel']
        cell_index = payload['cell_index']
        notebook = nb.reads(json.dumps(payload['notebook']), nb.NO_CONVERT)

        # extractor based on the kernel
        extractor = None
        if kernel == "IRkernel":
            extractor = RExtractor(notebook)
        else:
            extractor = Extractor(notebook)

        # initialize variables
        source = notebook.cells[cell_index].source
        title = source.partition('\n')[0]
        title = title.replace('#', '').replace('.', '-').replace(
            '_', '-').replace('(', '-').replace(')', '-').strip() if title and title[0] == "#" else "Untitled"

        if 'JUPYTERHUB_USER' in os.environ:
            title += '-' + os.environ['JUPYTERHUB_USER'].replace('_', '-').replace('(', '-').replace(')', '-').replace('.', '-').replace('@',
                                                                                                     '-at-').strip()

        ins = []
        outs = []
        params = []
        confs = []
        dependencies = []

        # Check if cell is code. If cell is for example markdown we get execution from 'extractor.infere_cell_inputs(
        # source)'
        if notebook.cells[cell_index].cell_type == 'code':
            dependencies = extractor.infer_cell_dependencies(source, confs)
            ins = set(extractor.infere_cell_inputs(source)) 
            outs = set(extractor.infere_cell_outputs(source))

            confs = extractor.extract_cell_conf_ref(source)

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
            container_source=""
        )
        if notebook.cells[cell_index].cell_type == 'code':
            cell.integrate_configuration()
            params = list(extractor.extract_cell_params(cell.original_source))
            cell.params = params
    
        node = ConverterReactFlowChart.get_node(
            node_id,
            title,
            ins,
            outs,
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

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        port = payload['port']
        p_type = payload['type']
        cell = Catalog.editor_buffer
        cell.types[port] = p_type


class BaseImageHandler(APIHandler, Catalog):

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        base_image = payload['image']
        cell = Catalog.editor_buffer
        cell.base_image = base_image


def find_job(wf_id=None, owner=None, repository_name=None, token=None, job_id=None):
    if job_id:
        jobs_url = github_url_repos + '/' + owner + '/' + repository_name + '/actions/jobs/' + str(job_id)
        job = get_github_workflow_jobs(jobs_url, token=token)
        return job
    last_minutes = str(
        (datetime.datetime.now() - datetime.timedelta(hours=0, minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ"))
    runs = get_github_workflow_runs(owner=owner, repository_name=repository_name, last_minutes=last_minutes,
                                    token=token)
    if not runs:
        return None
    for run in runs['workflow_runs']:
        jobs_url = run['jobs_url']
        jobs = get_github_workflow_jobs(jobs_url)
        for job in jobs['jobs']:
            if job['name'] == wf_id:
                return job
    return None

# Add to the catalog
class CellsHandler(APIHandler, Catalog):
    logger = logging.getLogger(__name__)

    @web.authenticated
    async def get(self):
        msg_json = dict(title='Operation not supported.')
        self.write(msg_json)
        self.flush()

    @web.authenticated
    async def post(self, *args, **kwargs):
        current_cell = Catalog.editor_buffer
        current_cell.clean_code()
        current_cell.clean_title()
        current_cell.clean_task_name()

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

        logger.debug('Delete if exists: ' + current_cell.task_name)
        Catalog.delete_cell_from_task_name(current_cell.task_name)
        Catalog.add_cell(current_cell)

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

        # TODO: I need credentials from Spiros. Uncomment stuff from below
        # registry_credentials = Catalog.get_registry_credentials()
        # if not registry_credentials or len(registry_credentials) <= 0:
        #     self.set_status(400)
        #     self.write_error('Registry credentials not found')
        #     logger.error('Registry credentials not found')
        #     self.flush()
        #     return
        # registry_url = registry_credentials[0]['url']
        # if not registry_url:
        #     self.set_status(400)
        #     self.write_error('Registry url not found')
        #     logger.error('Registry url not found')
        #     self.flush()
        #     return
        # image_repo = registry_url.split(
        #     'https://hub.docker.com/u/')[1]
        image_repo = "dedder123" # TODO: Remove this later

        # handle request
        payload = self.get_json_body()
        kernel = payload['kernel']

        # extractor based on the kernel
        files_info = None
        if kernel == "IRkernel":
            files_info = Rcontainerizer.get_files_info(cell=current_cell, image_repo=image_repo, cells_path=cells_path) 
            Rcontainerizer.build_templates(cell=current_cell, files_info=files_info)
        else:
            files_info = get_files_info(cell=current_cell, image_repo=image_repo) 
            build_templates(cell=current_cell, files_info=files_info)

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

        commit = gh_repository.get_commits(path=current_cell.task_name)

        if commit.totalCount > 0:
            try:
                update_cell_in_repository(task_name=current_cell.task_name, repository=gh_repository,
                                          files_info=files_info)
            except UnknownObjectException as ex:
                create_cell_in_repository(task_name=current_cell.task_name, repository=gh_repository,
                                          files_info=files_info)
        elif commit.totalCount <= 0:
            create_cell_in_repository(task_name=current_cell.task_name, repository=gh_repository,
                                      files_info=files_info)

        wf_id = str(uuid.uuid4())
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
        self.write(json.dumps({'wf_id': wf_id}))
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
    for f_type, f_info in files_info.items():
        f_name = f_info['file_name']
        f_path = f_info['path']
        logger.debug('get_contents: ' + task_name + '/' + f_name)
        print('get_contents: ' + task_name + '/' + f_name)
        remote_content = repository.get_contents(
            path=task_name + '/' + f_name)
        with open(f_path, 'rb') as f:
            local_content = f.read()
            local_hash = git_hash(local_content)
            remote_hash = remote_content.sha
            logger.debug('local_hash: ' + local_hash + ' remote_hash: ' + remote_hash)
            if remote_hash != local_hash:
                repository.update_file(
                    path=task_name + '/' + f_name,
                    message=task_name + ' update',
                    content=local_content,
                    sha=remote_content.sha
                )
        f.close()


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


def get_github_workflow_runs(owner=None, repository_name=None, last_minutes=None, token=None):
    workflow_runs_url = github_url_repos + '/' + owner + '/' + repository_name + '/actions/runs'
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

    template_cell = template_env.get_template('cell_template.jinja2') # TODO: look at these templates
    template_dockerfile = template_env.get_template(
        'dockerfile_template_conda.jinja2')
    template_conda = template_env.get_template('conda_env_template.jinja2')

    compiled_code = template_cell.render(cell=cell, deps=cell.generate_dependencies(), types=cell.types,
                                         confs=cell.generate_configuration())
    compiled_code = autopep8.fix_code(compiled_code)
    cell.container_source = compiled_code

    template_cell.stream(cell=cell, deps=cell.generate_dependencies(), types=cell.types,
                         confs=cell.generate_configuration()).dump(files_info['cell']['path']) # TODO: the variables are set here
    template_dockerfile.stream(task_name=cell.task_name, base_image=cell.base_image).dump(
        files_info['dockerfile']['path'])
    template_conda.stream(base_image=cell.base_image, conda_deps=list(set_conda_deps),
                          pip_deps=list(set_pip_deps)).dump(files_info['environment']['path'])


def get_files_info(cell=None, image_repo=None):
    if not os.path.exists(cells_path):
        os.mkdir(cells_path)
    cell_path = os.path.join(cells_path, cell.task_name)

    cell_file_name = cell.task_name + '.py'
    dockerfile_name = 'Dockerfile.' + image_repo + '.' + cell.task_name
    environment_file_name = cell.task_name + '-environment.yaml'

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
    return {'cell': {
        'file_name': cell_file_name,
        'path': cell_file_path},
        'dockerfile': {
            'file_name': dockerfile_name,
            'path': dockerfile_file_path},
        'environment': {
            'file_name': environment_file_name,
            'path': env_file_path}
    }