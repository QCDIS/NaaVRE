import copy
import json
import logging
import os
import uuid
from pathlib import Path

import autopep8
import github3
import nbformat as nb
import requests
from github3 import login
from jinja2 import Environment, PackageLoader
from notebook.base.handlers import APIHandler
from tornado import web

from jupyterlab_vre.converter.converter import ConverterReactFlowChart
from jupyterlab_vre.extractor.extractor import Extractor
from jupyterlab_vre.faircell import Cell
from jupyterlab_vre.github.gh_credentials import GHCredentials
from jupyterlab_vre.sdia.sdia import SDIA
from jupyterlab_vre.sdia.sdia_credentials import SDIACredentials
from jupyterlab_vre.storage.catalog import Catalog
from jupyterlab_vre.workflows.parser import WorkflowParser

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
module_mapping = {'fnmatch': 'fnmatch2'}
standard_library = [
    'pathlib',
    'time',
    'os',
    'fileinput',
    'tempfile',
    'glob',
    'sys',
    'stat',
    'filecmp',
    'linecache',
    'shutil',
    'logging',
    'socket',
    'array',
    'ssl',
    'datetime',
    'smtplib',
    'selectors',
    'asyncio',
    'sys',
    'signal',
    'asynchat',
    'mmap',
    'multiprocessing',
    'concurrent',
    'urllib',
    'math',
    'shlex',
    'subprocess',
    'sched',
    'threading',
    'dummy_threading',
    'io',
    'argparse',
    'getopt',
    'random'
]

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
        cell_index = payload['cell_index']
        notebook = nb.reads(json.dumps(payload['notebook']), nb.NO_CONVERT)
        extractor = Extractor(notebook)

        source = notebook.cells[cell_index].source

        title = source.partition('\n')[0]
        title = title.replace('#', '').replace('_', '-').strip() if title[0] == "#" else "Untitled"

        ins = set(extractor.infere_cell_inputs(source))
        outs = set(extractor.infere_cell_outputs(source))
        params = []
        confs = extractor.extract_cell_conf_ref(source)
        dependencies = extractor.infere_cell_dependencies(source)
        conf_deps = extractor.infere_cell_conf_dependencies(confs)
        dependencies = dependencies + conf_deps
        node_id = str(uuid.uuid4())[:7]

        cell = Cell(
            node_id             = node_id,
            title               = title,
            task_name           = title.lower().replace(' ', '-'),
            original_source     = source,
            inputs              = ins,
            outputs             = outs,
            params              = params,
            confs               = confs,
            dependencies        = dependencies,
            container_source    = ""
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
                'x': -100,
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

        self.write(json.dumps({
            'node_id': node_id,
            'chart': chart,
            'deps': dependencies
        }))

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

# Catalog

################################################################################

def load_standard_library_names():
    standard_library_names_path = os.path.join(str(Path.home()), 'NaaVRE', 'standard_library_names.json')
    if not os.path.exists(standard_library_names_path):
        with open(standard_library_names_path, "w") as standard_library_names_file:
            json.dump(standard_library, standard_library_names_file, indent=4)
    standard_library_names_file = open(standard_library_names_path)
    part_of_standard_library = json.load(standard_library_names_file)
    return part_of_standard_library


def load_module_names_mapping():
    module_name_mapping_path = os.path.join(str(Path.home()), 'NaaVRE', 'module_name_mapping.json')
    if not os.path.exists(module_name_mapping_path):
        with open(module_name_mapping_path, "w") as module_name_mapping_file:
            json.dump(module_mapping, module_name_mapping_file, indent=4)
    module_name_mapping_file = open(module_name_mapping_path)
    module_name_mapping = json.load(module_name_mapping_file)
    return module_name_mapping


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
        loader = PackageLoader('jupyterlab_vre', 'templates')
        template_env = Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)

        template_cell = template_env.get_template('cell_template.jinja2')
        template_dockerfile = template_env.get_template('dockerfile_template_conda.jinja2')
        template_conda = template_env.get_template('conda_env_template.jinja2')

        all_vars = current_cell.params + current_cell.inputs + current_cell.outputs
        logger.debug('all_vars: ' + str(all_vars))
        for parm_name in all_vars:
            if parm_name not in current_cell.types:
                logger.error(parm_name + ' has not type')
                msg_json = dict(title=parm_name + ' has not type')
                self.set_status(400)
                self.write(parm_name + ' has not type')
                self.write_error(parm_name + ' has not type')
                self.flush()
                # or self.render("error.html", reason="You're not authorized"))
                return
                # raise tornado.web.HTTPError(400, reason=parm_name + ' has not type')

        compiled_code = template_cell.render(cell=current_cell, deps=deps, types=current_cell.types, confs=confs)
        compiled_code = autopep8.fix_code(compiled_code)
        current_cell.container_source = compiled_code

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

        cell_file_name = current_cell.task_name + '.py'
        dockerfile_name = 'Dockerfile.qcdis.' + current_cell.task_name
        env_name = current_cell.task_name + '-environment.yaml'

        part_of_standard_library = load_standard_library_names()
        module_name_mapping = load_module_names_mapping()
        set_deps = set([])
        for dep in current_cell.dependencies:
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
                if module_name not in part_of_standard_library:
                    set_deps.add(module_name)

        # set_deps = set([dep['module'].split('.')[0] for dep in current_cell.dependencies])

        cell_file_path = os.path.join(cell_path, cell_file_name)
        dockerfile_file_path = os.path.join(cell_path, dockerfile_name)
        env_file_path = os.path.join(cell_path, env_name)
        files_info = {cell_file_name: cell_file_path, dockerfile_name: dockerfile_file_path, env_name: env_file_path}

        template_cell.stream(cell=current_cell, deps=deps, types=current_cell.types, confs=confs).dump(cell_file_path)
        template_dockerfile.stream(task_name=current_cell.task_name).dump(dockerfile_file_path)
        template_conda.stream(deps=list(set_deps)).dump(os.path.join(cell_path, env_name))

        credentials = Catalog.get_gh_credentials()
        if not credentials:
            self.set_status(400)
            self.write('Github credentials are not set!')
            self.write_error('Github credentials are not set!')
            self.flush()
            # or self.render("error.html", reason="You're not authorized"))
            return
        logger.debug('credentials: '+str(credentials))
        gh = login(token=credentials['token'])
        owner = credentials['url'].split('https://github.com/')[1].split('/')[0]
        repository_name = credentials['url'].split('https://github.com/')[1].split('/')[1]
        if '.git' in repository_name:
            repository_name = repository_name.split('.git')[0]
        logger.debug('owner: '+owner+' repository_name: '+repository_name)
        try:
            repository = gh.repository(owner, repository_name)
        except github3.exceptions.AuthenticationFailed as ex:
            self.set_status(400)
            if hasattr(ex, 'message'):
                self.write(ex.message)
            else:
                self.write(str(ex))
            self.write_err
            self.flush()
            return

        last_comm = next(repository.commits(number=1), None)

        if last_comm:
            last_tree_sha = last_comm.commit.tree.sha
            tree = repository.tree(last_tree_sha)
            paths = []

            for comm_file in tree.tree:
                paths.append(comm_file.path)

        if current_cell.task_name in paths:
            print('Cell is already in repository')
            # TODO: Update file
        else:
            print('Cell is not in repository')
            for f_name, f_path in files_info.items():
                with open(f_path, 'rb') as f:
                    content = f.read()
                    repository.create_file(
                        path=current_cell.task_name + '/' + f_name,
                        message=current_cell.task_name + ' creation',
                        content=content,
                    )

            resp = requests.post(
                url='https://api.github.com/repos/'+owner+'/'+repository_name+'/actions/workflows/build-push-docker'
                                                                              '.yml/dispatches',
                json={
                    "ref": "refs/heads/main",
                    "inputs": {
                        "build_dir": current_cell.task_name,
                        "dockerfile": dockerfile_name,
                        "image_repo": "qcdis",
                        "image_tag": current_cell.task_name
                    }
                },
                verify=False,
                headers={"Accept": "application/vnd.github.v3+json", "Authorization": "token " + credentials['token']}
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
        if payload and 'github-auth-token' in payload and 'github-url' in payload:
            Catalog.add_gh_credentials(
                GHCredentials(token=payload['github-auth-token'], url=payload['github-url'])
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
        print(resp)

        self.flush()


################################################################################

# Workflows

################################################################################


class ExportWorkflowHandler(APIHandler):

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        print(payload)
        global_params = []

        nodes = payload['nodes']
        links = payload['links']

        parser = WorkflowParser(nodes, links)
        cells = parser.get_workflow_cells()

        deps_dag = parser.get_dependencies_dag()

        for nid, cell in cells.items():
            global_params.extend(cell['params'])

        loader = PackageLoader('jupyterlab_vre', 'templates')
        template_env = Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)
        template = template_env.get_template('workflow_template_v2.jinja2')

        template.stream(
            deps_dag=deps_dag, 
            cells=cells,
            nodes=nodes,
            global_params=set(global_params)

        ).dump('workflow.yaml')
        self.flush()
