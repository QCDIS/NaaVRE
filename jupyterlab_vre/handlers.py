import copy
import hashlib
import importlib
import json
import logging
import os
import sys
import uuid
from builtins import Exception
from pathlib import Path
import distro

import autopep8
import nbformat as nb
import requests
from github import Github
from jinja2 import Environment, PackageLoader
from notebook.base.handlers import APIHandler
from tornado import web

from jupyterlab_vre.converter.converter import ConverterReactFlowChart
from jupyterlab_vre.extractor.extractor import Extractor
from jupyterlab_vre.storage.faircell import Cell

from jupyterlab_vre.repository.repository_credentials import RepositoryCredentials
from jupyterlab_vre.sdia.sdia import SDIA
from jupyterlab_vre.sdia.sdia_credentials import SDIACredentials
from jupyterlab_vre.storage.catalog import Catalog
from jupyterlab_vre.workflows.parser import WorkflowParser

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
module_mapping = {
    "torch.nn": "torch",
    "torchvision.models": "torchvision",
    "cv2": "opencv-python-headless"
}

if 'JUPYTERHUB_USER' in os.environ:
    current_username = os.environ['JUPYTERHUB_USER']


# code from https://stackoverflow.com/questions/552659/how-to-assign-a-git-sha1s-to-a-file-without-git
def git_hash(contents):
    s = hashlib.sha1()
    s.update(("blob %u\0" % len(contents)).encode('utf-8'))
    s.update(contents)
    return s.hexdigest()


################################################################################

# Extraction

################################################################################

class ExtractorHandler(APIHandler, Catalog):
    logger = logging.getLogger(__name__)

    @web.authenticated
    async def get(self):
        msg_json = dict(title="Operation not supported.")
        self.write(msg_json)
        self.flush()

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        logger.debug('payload: ' + json.dumps(payload))
        cell_index = payload['cell_index']
        notebook = nb.reads(json.dumps(payload['notebook']), nb.NO_CONVERT)
        extractor = Extractor(notebook)

        source = notebook.cells[cell_index].source

        title = source.partition('\n')[0]
        title = title.replace('#', '').replace('_', '-').replace('(', '-').replace(')', '-').strip() if title[
                                                                                                            0] == "#" else "Untitled"
        if current_username:
            title += '.'+current_username
        ins = set(extractor.infer_cell_inputs(source))
        outs = set(extractor.infer_cell_outputs(source))
        params = []
        logger.debug('outs: ' + str(outs))
        confs = extractor.extract_cell_conf_ref(source)
        dependencies = extractor.infer_cell_dependencies(source, confs)
        # conf_deps = extractor.infere_cell_conf_dependencies(confs)
        # dependencies = dependencies + conf_deps
        node_id = str(uuid.uuid4())[:7]
        cell = Cell(
            node_id=node_id,
            title=title,
            task_name=title.lower().replace(' ', '-'),
            original_source=source,
            inputs=ins,
            outputs=outs,
            params=params,
            confs=confs,
            dependencies=dependencies,
            container_source=""
        )

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


class NotebookExtractorHandler(APIHandler, Catalog):
    logger = logging.getLogger(__name__)

    @web.authenticated
    async def get(self):
        msg_json = dict(title="Operation not supported.")
        self.write(msg_json)
        self.flush()

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        notebook = nb.reads(json.dumps(payload['notebook']), nb.NO_CONVERT)
        extractor = Extractor(notebook)
        source = ''
        params = set()
        confs = set()
        ins = set()
        outs = set(extractor.infer_cell_outputs(notebook.cells[len(notebook.cells) - 1].source))
        for cell_source in extractor.sources:
            p = extractor.extract_cell_params(cell_source)
            params.update(p)
            c = extractor.extract_cell_conf_ref(source)
            confs.update(c)
            source += cell_source + '\n'

        title = 'notebook-'+notebook.cells[0].source.partition('\n')[0]
        title = title.replace('#', '').replace('_', '-').replace('(', '-').replace(')', '-').strip() if title[
                                                                                                            0] == "#" else "Untitled"
        dependencies = extractor.infer_cell_dependencies(source, confs)

        node_id = str(uuid.uuid4())[:7]
        cell = Cell(
            node_id=node_id,
            title=title,
            task_name=title.lower().replace(' ', '-'),
            original_source=source,
            inputs=list(ins),
            outputs=list(outs),
            params=list(params),
            confs=list(confs),
            dependencies=list(dependencies),
            container_source=""
        )
        cell.integrate_configuration()
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


################################################################################

# Types

################################################################################

class TypesHandler(APIHandler, Catalog):

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        port = payload['port']
        p_type = payload['type']
        cell = Catalog.editor_buffer
        cell.types[port] = p_type


################################################################################

# Base Image

################################################################################

class BaseImageHandler(APIHandler, Catalog):

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        logger.debug('payload: ' + str(payload))
        base_image = payload['image']
        cell = Catalog.editor_buffer
        cell.base_image = base_image


################################################################################

# Catalog

################################################################################
def is_standard_module(module_name):
    if module_name in sys.builtin_module_names:
        return True
    installation_path = None
    try:
        installation_path = importlib.import_module(module_name).__file__
    except ImportError:
        return False
    linux_os = distro.id()
    return "dist-packages" not in installation_path if linux_os == "Ubuntu" else "site-packages" not in installation_path


def load_module_names_mapping():
    module_name_mapping_path = os.path.join(str(Path.home()), 'NaaVRE', 'module_name_mapping.json')
    if not os.path.exists(module_name_mapping_path):
        with open(module_name_mapping_path, "w") as module_name_mapping_file:
            json.dump(module_mapping, module_name_mapping_file, indent=4)
    module_name_mapping_file = open(module_name_mapping_path)
    loaded_module_name_mapping = json.load(module_name_mapping_file)
    loaded_module_name_mapping.update(module_mapping)
    return loaded_module_name_mapping


def build_templates(cell=None, files_info=None):
    logger.debug('files_info: '+str(files_info))
    module_name_mapping = load_module_names_mapping()
    set_deps = set([])
    for dep in cell.dependencies:
        if 'module' in dep and dep['module']:
            if '.' in dep['module']:
                module_name = dep['module'].split('.')[0]
            else:
                module_name = dep['module']
        elif 'name' in dep and dep['name']:
            module_name = dep['name']
        if module_name:
            if module_name in module_name_mapping.keys():
                module_name = module_name_mapping[module_name]
            if not is_standard_module(module_name):
                set_deps.add(module_name)

    loader = PackageLoader('jupyterlab_vre', 'templates')
    template_env = Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)

    template_cell = template_env.get_template('cell_template.jinja2')
    template_dockerfile = template_env.get_template('dockerfile_template_conda.jinja2')
    template_conda = template_env.get_template('conda_env_template.jinja2')

    compiled_code = template_cell.render(cell=cell, deps=cell.generate_dependencies(), types=cell.types,
                                         confs=cell.generate_configuration())
    compiled_code = autopep8.fix_code(compiled_code)
    cell.container_source = compiled_code

    template_cell.stream(cell=cell, deps=cell.generate_dependencies(), types=cell.types,
                         confs=cell.generate_configuration()).dump(files_info['cell']['path'])
    template_dockerfile.stream(task_name=cell.task_name, base_image=cell.base_image).dump(
        files_info['dockerfile']['path'])
    template_conda.stream(base_image=cell.base_image, deps=list(set_deps)).dump(files_info['environment']['path'])

def get_files_info(cell=None, image_repo=None):
    cells_path = os.path.join(str(Path.home()), 'NaaVRE', 'cells')
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


class CellsHandler(APIHandler, Catalog):
    logger = logging.getLogger(__name__)

    @web.authenticated
    async def get(self):
        msg_json = dict(title="Operation not supported.")
        self.write(msg_json)
        self.flush()

    @web.authenticated
    async def post(self, *args, **kwargs):

        current_cell = Catalog.editor_buffer
        deps = current_cell.generate_dependencies()
        confs = current_cell.generate_configuration()
        current_cell.clean_code()

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
            logger.error(current_cell.task_name + ' has not base image not selected')
            self.set_status(400)
            self.write(current_cell.task_name + ' has not base image selected')
            self.write_error(current_cell.task_name + ' has not base not image selected')
            self.flush()
            return

        logger.debug('Delete if exists: ' + current_cell.task_name)
        Catalog.delete_cell_from_task_name(current_cell.task_name)
        Catalog.add_cell(current_cell)

        cells_path = os.path.join(str(Path.home()), 'NaaVRE', 'cells')

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
        logger.debug('registry_credentials: ' + str(registry_credentials))
        if not registry_credentials:
            self.set_status(400)
            self.write('Registry credentials are not set!')
            self.write_error('Registry credentials are not set!')
            self.flush()
            return
        image_repo = registry_credentials['url'].split('https://hub.docker.com/u/')[1]

        files_info = get_files_info(cell=current_cell, image_repo=image_repo)

        build_templates(cell=current_cell, files_info=files_info)

        gh_credentials = Catalog.get_gh_credentials()
        logger.debug('gh_credentials: ' + str(gh_credentials))
        if not gh_credentials:
            self.set_status(400)
            self.write('Github gh_credentials are not set!')
            self.write_error('Github credentials are not set!')
            self.flush()
            # or self.render("error.html", reason="You're not authorized"))
            return

        gh = Github(gh_credentials['token'])
        owner = gh_credentials['url'].split('https://github.com/')[1].split('/')[0]
        repository_name = gh_credentials['url'].split('https://github.com/')[1].split('/')[1]
        if '.git' in repository_name:
            repository_name = repository_name.split('.git')[0]
        logger.debug('owner: ' + owner + ' repository_name: ' + repository_name)
        try:
            repository = gh.get_repo(owner + '/' + repository_name)
        except Exception as ex:
            self.set_status(400)
            if hasattr(ex, 'message'):
                self.write(ex.message)
            else:
                self.write(str(ex))
            self.write_err
            self.flush()
            return

        commit = repository.get_commits(path=current_cell.task_name)
        if commit.totalCount > 0:
            logger.debug('Cell is in repository')
            for f_type, f_info in files_info.items():
                f_name = f_info['file_name']
                f_path = f_info['path']
                remote_content = repository.get_contents(path=current_cell.task_name + '/' + f_name)
                with open(f_path, 'rb') as f:
                    local_content = f.read()
                    local_hash = git_hash(local_content)
                    if remote_content.sha != git_hash(local_content):
                        repository.update_file(
                            path=current_cell.task_name + '/' + f_name,
                            message=current_cell.task_name + ' update',
                            content=local_content,
                            sha=remote_content.sha
                        )
        elif commit.totalCount <= 0:
            logger.debug('Cell is not in repository')
            for f_type, f_info in files_info.items():
                f_name = f_info['file_name']
                f_path = f_info['path']
                with open(f_path, 'rb') as f:
                    content = f.read()
                    repository.create_file(
                        path=current_cell.task_name + '/' + f_name,
                        message=current_cell.task_name + ' creation',
                        content=content,
                    )
        resp = requests.post(
            url='https://api.github.com/repos/' + owner + '/' + repository_name + '/actions/workflows/build-push-docker'
                                                                                  '.yml/dispatches',
            json={
                "ref": "refs/heads/main",
                "inputs": {
                    "build_dir": current_cell.task_name,
                    "dockerfile": files_info['dockerfile']['file_name'],
                    "image_repo": image_repo,
                    "image_tag": current_cell.task_name
                }
            },
            verify=False,
            headers={"Accept": "application/vnd.github.v3+json",
                     "Authorization": "token " + gh_credentials['token']}
        )
        self.flush()

    @web.authenticated
    async def delete(self, *args, **kwargs):
        payload = self.get_json_body()
        Catalog.delete_cell_from_title(payload['title'])


class CatalogGetAllHandler(APIHandler, Catalog):

    @web.authenticated
    async def get(self):
        self.write(json.dumps(Catalog.get_all_cells()))
        self.flush()

    @web.authenticated
    async def post(self, *args, **kwargs):
        msg_json = dict(title="Operation not supported.")
        self.write(msg_json)
        self.flush()


################################################################################

# SDIA Auth

################################################################################

class SDIAAuthHandler(APIHandler, SDIA, Catalog):

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        reply = {}
        res = SDIA.test_auth(payload['sdia-auth-username'], payload['sdia-auth-password'],
                             payload['sdia-auth-endpoint'])
        error = issubclass(type(res), Exception)

        if not error:
            Catalog.add_sdia_credentials(
                SDIACredentials(
                    username=payload['sdia-auth-username'],
                    password=payload['sdia-auth-password'],
                    endpoint=payload['sdia-auth-endpoint']
                )
            )

        reply['message'] = str(res) if error else 'Credentials Saved'
        self.write(reply)
        self.flush()


################################################################################

# Github  Auth

################################################################################


class GithubAuthHandler(APIHandler, Catalog):

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        logger.debug('GithubAuthHandler payload: ' + str(payload))
        if payload and 'github-auth-token' in payload and 'github-url' in payload:
            logger.debug('Catalog.delete_all_gh_credentials()')
            Catalog.delete_all_gh_credentials()
            Catalog.add_gh_credentials(
                RepositoryCredentials(token=payload['github-auth-token'], url=payload['github-url'])
            )
        self.flush()


################################################################################

# Image Registry  Auth

################################################################################
class ImageRegistryAuthHandler(APIHandler, Catalog):

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        logger.debug('ImageRegistryAuthHandler payload: ' + str(payload))
        if payload and 'image-registry-url' in payload:
            Catalog.delete_all_registry_credentials()
            Catalog.add_registry_credentials(
                RepositoryCredentials(url=payload['image-registry-url'])
            )
        self.flush()


################################################################################

# SDIA Credentials

################################################################################


class SDIACredentialsHandler(APIHandler, Catalog):

    @web.authenticated
    async def get(self, *args, **kwargs):
        self.write(json.dumps(Catalog.get_sdia_credentials()))
        self.flush()


################################################################################

# Automator

################################################################################

class ProvisionAddHandler(APIHandler, Catalog, SDIA):

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        cred_username = payload['credential']
        template_id = payload['provision_template']
        credentials = Catalog.get_credentials_from_username(cred_username)

        resp = SDIA.provision(credentials, template_id)
        self.flush()


################################################################################

# Workflows

################################################################################

class ExportWorkflowHandler(APIHandler):

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        logger.debug('payload: ' + str(payload))
        global_params = []

        nodes = payload['nodes']
        links = payload['links']

        parser = WorkflowParser(nodes, links)
        cells = parser.get_workflow_cells()

        deps_dag = parser.get_dependencies_dag()
        logger.debug('deps_dag: ' + str(deps_dag))

        for nid, cell in cells.items():
            global_params.extend(cell['params'])

        registry_credentials = Catalog.get_registry_credentials()

        if not registry_credentials:
            self.set_status(400)
            self.write('Registry credentials are not set!')
            self.write_error('Registry credentials are not set!')
            self.flush()
            return

        image_repo = registry_credentials['url'].split('https://hub.docker.com/u/')[1]
        loader = PackageLoader('jupyterlab_vre', 'templates')
        template_env = Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)
        template = template_env.get_template('workflow_template_v2.jinja2')

        template.stream(
            deps_dag=deps_dag,
            cells=cells,
            nodes=nodes,
            global_params=set(global_params),
            image_repo=image_repo

        ).dump('workflow.yaml')
        self.flush()
