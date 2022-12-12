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
from jupyterlab_vre.services.extractor.extractor import Extractor
from notebook.base.handlers import APIHandler
from tornado import web

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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
        payload = self.get_json_body()
        print(json.dumps(payload))
        cell_index = payload['cell_index']
        notebook = nb.reads(json.dumps(payload['notebook']), nb.NO_CONVERT)
        extractor = Extractor(notebook)

        source = notebook.cells[cell_index].source
        title = source.partition('\n')[0]
        title = title.replace('#', '').replace(
            '_', '-').replace('(', '-').replace(')', '-').strip() if title and title[0] == "#" else "Untitled"

        if 'JUPYTERHUB_USER' in os.environ:
            title += '-' + os.environ['JUPYTERHUB_USER']
            title.replace('_', '-').replace('(', '-').replace(')', '-').strip()

        ins = []
        outs = []
        params = []
        confs = []
        dependencies = []

        # Check if cell is code. If cell is for example markdown we get execution from 'extractor.infere_cell_inputs(source)'
        if notebook.cells[cell_index].cell_type == 'code':
            ins = set(extractor.infere_cell_inputs(source))
            outs = set(extractor.infere_cell_outputs(source))

            confs = extractor.extract_cell_conf_ref(source)
            dependencies = extractor.infer_cell_dependencies(source, confs)

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

        registry_credentials = registry_credentials = Catalog.get_registry_credentials()
        logger.debug('registry_credentials: ' + str(registry_credentials[0]))

        image_repo = registry_credentials[0]['url'].split(
            'https://hub.docker.com/u/')[1]

        files_info = get_files_info(cell=current_cell, image_repo=image_repo)

        print(current_cell)
        build_templates(cell=current_cell, files_info=files_info)

        repository = Catalog.get_repositories()

        repo_token = repository[0]['token']

        gh = Github(repository[0]['token'])
        owner = repository[0]['url'].split('https://github.com/')[1].split('/')[0]
        repository_name = repository[0]['url'].split(
            'https://github.com/')[1].split('/')[1]
        if '.git' in repository_name:
            repository_name = repository_name.split('.git')[0]
        logger.debug('owner: ' + owner +
                     ' repository_name: ' + repository_name)
        try:
            repository = gh.get_repo(owner + '/' + repository_name)
        except Exception as ex:
            self.set_status(400)
            if hasattr(ex, 'message'):
                self.write(ex.message)
            else:
                self.write(str(ex))
            self.flush()
            return

        commit = repository.get_commits(path=current_cell.task_name)

        if commit.totalCount > 0:
            try:
                update_cell_in_repository(current_cell, repository, files_info)
            except UnknownObjectException as ex:
                create_cell_in_repository(current_cell, repository, files_info)
        elif commit.totalCount <= 0:
            create_cell_in_repository(current_cell, repository, files_info)

        resp = dispatch_github_workflow(
            owner,
            repository_name,
            current_cell,
            files_info,
            repo_token,
            image_repo
        )

        self.flush()


def create_cell_in_repository(cell, repository, files_info):
    for f_type, f_info in files_info.items():
        f_name = f_info['file_name']
        f_path = f_info['path']
        with open(f_path, 'rb') as f:
            content = f.read()
            repository.create_file(
                path=cell.task_name + '/' + f_name,
                message=cell.task_name + ' creation',
                content=content,
            )


def update_cell_in_repository(cell, repository, files_info):
    for f_type, f_info in files_info.items():
        f_name = f_info['file_name']
        f_path = f_info['path']
        remote_content = repository.get_contents(
            path=cell.task_name + '/' + f_name)
        with open(f_path, 'rb') as f:
            local_content = f.read()
            local_hash = git_hash(local_content)
            if remote_content.sha != git_hash(local_content):
                repository.update_file(
                    path=cell.task_name + '/' + f_name,
                    message=cell.task_name + ' update',
                    content=local_content,
                    sha=remote_content.sha
                )


def dispatch_github_workflow(owner, repository_name, cell, files_info, repository_token, image):
    return requests.post(
        url='https://api.github.com/repos/' + owner + '/' +
            repository_name + '/actions/workflows/build-push-docker'
                              '.yml/dispatches',
        json={
            'ref': 'refs/heads/main',
            'inputs': {
                'build_dir': cell.task_name,
                'dockerfile': files_info['dockerfile']['file_name'],
                'image_repo': image,
                'image_tag': cell.task_name
            }
        },
        verify=False,
        headers={'Accept': 'application/vnd.github.v3+json',
                 'Authorization': 'token ' + repository_token}
    )


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

    module_name_mapping_file = open(module_name_mapping_path)
    loaded_module_name_mapping = json.load(module_name_mapping_file)
    loaded_module_name_mapping.update(module_mapping)
    return loaded_module_name_mapping


def build_templates(cell=None, files_info=None):
    logger.debug('files_info: ' + str(files_info))
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
    template_env = Environment(
        loader=loader, trim_blocks=True, lstrip_blocks=True)

    template_cell = template_env.get_template('cell_template.jinja2')
    template_dockerfile = template_env.get_template(
        'dockerfile_template_conda.jinja2')
    template_conda = template_env.get_template('conda_env_template.jinja2')

    compiled_code = template_cell.render(cell=cell, deps=cell.generate_dependencies(), types=cell.types,
                                         confs=cell.generate_configuration())
    compiled_code = autopep8.fix_code(compiled_code)
    cell.container_source = compiled_code

    template_cell.stream(cell=cell, deps=cell.generate_dependencies(), types=cell.types,
                         confs=cell.generate_configuration()).dump(files_info['cell']['path'])
    template_dockerfile.stream(task_name=cell.task_name, base_image=cell.base_image).dump(
        files_info['dockerfile']['path'])
    template_conda.stream(base_image=cell.base_image, deps=list(
        set_deps)).dump(files_info['environment']['path'])


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
