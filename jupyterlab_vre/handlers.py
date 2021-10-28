import os
import tarfile
import copy
import json
import shutil
from requests.models import HTTPBasicAuth
import yaml
import uuid
import requests
import nbformat as nb
import autopep8
from notebook.base.handlers import APIHandler
from tornado import web
from datetime import datetime, timedelta
from jupyterlab_vre.extractor.extractor import Extractor
from jupyterlab_vre.converter.converter import ConverterReactFlowChart
from jupyterlab_vre.sdia.sdia import SDIA
from jupyterlab_vre.faircell import Cell
from jupyterlab_vre.storage.catalog import Catalog
from jupyterlab_vre.storage.azure import AzureStorage
from jupyterlab_vre.workflows.parser import WorkflowParser
from jinja2 import Environment, PackageLoader, FileSystemLoader

################################################################################

                            # Extraction

################################################################################

class ExtractorHandler(APIHandler, Catalog):

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
        title = title.replace('#', '').strip() if title[0] == "#" else "Untitled"
        
        ins = set(extractor.infere_cell_inputs(source))
        outs = set(extractor.infere_cell_outputs(source))
        params = []
        confs = extractor.extract_cell_conf_ref(source)

        dependencies = extractor.infere_cell_dependencies(source)

        cell = Cell(
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

        node_id = str(uuid.uuid4())[:7]
        node = ConverterReactFlowChart.get_node(
            node_id, 
            title, 
            ins, 
            outs, 
            params, 
            dependencies
        )

        print(dependencies)

        chart = {
            'offset': {
                'x': -100,
                'y': 0,
            },
            'scale': 1,
            'nodes': { node_id: node },
            'links': {},
            'selected': {},
            'hovered': {},
        }

        cell.node_id = node_id
        cell.chart_obj = chart

        Catalog.editor_buffer = copy.deepcopy(cell)

        self.write(json.dumps({
            'node_id'   : node_id,
            'chart'     : chart,
            'deps'      : dependencies
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

class CellsHandler(APIHandler, Catalog):

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
        template_dockerfile = template_env.get_template('dockerfile_template.jinja2')
        template_conda = template_env.get_template('conda_env_template.jinja2')

        compiled_code = template_cell.render(cell=current_cell, deps=deps, types=current_cell.types, confs=confs)
        compiled_code = autopep8.fix_code(compiled_code)
        current_cell.container_source = compiled_code

        Catalog.add_cell(current_cell)

        cell_temp_path = "./%s" % current_cell.task_name
        os.mkdir(cell_temp_path)

        cell_file_name = current_cell.task_name + '.py'
        context_name = current_cell.task_name + '-context.tar.gz'
        dockerfile_name = current_cell.task_name + '-dockerfile'
        env_name = current_cell.task_name + '-environment.yaml'

        set_deps = set([dep['module'].split('.')[0] for dep in current_cell.dependencies])
        print(current_cell.params)

        template_cell.stream(cell=current_cell, deps=deps, types=current_cell.types, confs=confs).dump(os.path.join(cell_temp_path, cell_file_name))
        template_conda.stream(deps=list(set_deps)).dump(os.path.join(cell_temp_path, env_name))
        template_dockerfile.stream(task_name=current_cell.task_name).dump(dockerfile_name)

        with tarfile.open(context_name, 'w:gz') as tar:
            tar.add(cell_temp_path, arcname=os.path.sep)

        # AzureStorage.test_upload(file_path=context_name, container_name='test-container')
        # AzureStorage.test_upload(file_path=dockerfile_name, container_name='test-container')

        # os.remove(context_name)
        # os.remove(dockerfile_name)
        # shutil.rmtree(cell_temp_path)

        # tosca_res = requests.get(
        #     'https://lifewatch.lab.uvalight.net:30003/orchestrator/tosca_template/61450d4a55804f310896f954',
        #     auth=HTTPBasicAuth('', ''),
        #     verify=False
        # )

        # tosca = yaml.safe_load(tosca_res.content)

        # tosca['topology_template']['node_templates']['kaniko']['interfaces'] \
        #         ['Helm']['install_chart']['inputs']['extra_variables']['values']['context'] = \
        #         'https://lwdatasetstorage.blob.core.windows.net/test-container/' + context_name

        # tosca['topology_template']['node_templates']['kaniko']['interfaces'] \
        #         ['Helm']['install_chart']['inputs']['extra_variables']['values']['dockerfile'] = \
        #         'https://lwdatasetstorage.blob.core.windows.net/test-container/' + dockerfile_name

        # tosca['topology_template']['node_templates']['kaniko']['interfaces'] \
        #         ['Helm']['install_chart']['inputs']['extra_variables']['values']['destination'] = \
        #         'qcdis/' + current_cell.task_name

        # with open('tosca_edited.yaml', 'w') as tosca_file:
        #     yaml.dump(tosca, tosca_file)
        
        # upload_file = {'file': ('tosca.yaml', open('tosca_edited.yaml', 'rb'), 'text/yaml')}

        # up_res = requests.post(
        #     'https://lifewatch.lab.uvalight.net:30003/orchestrator/tosca_template/',
        #     auth=HTTPBasicAuth('', ''),
        #     verify=False,
        #     files=upload_file
        # )

        # os.remove('tosca_edited.yaml')

        # deploy_res = requests.get(
        #     'https://lifewatch.lab.uvalight.net:30003/orchestrator/deployer/deploy/' + up_res.text,
        #     auth=HTTPBasicAuth('', ''),
        #     verify=False
        # )

        self.flush()
        

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

class SDIAAuthHandler(APIHandler, SDIA):

    @web.authenticated
    async def post(self, *args, **kwargs):
        
        payload = self.get_json_body()

        try:
            res = SDIA.test_auth(payload['sdia-auth-username'], payload['sdia-auth-password'], payload['sdia-auth-endpoint'])
            self.finish(res)
            self.flush()
        except Exception as ex:
            print("In ex")
            self.finish(json.dumps(str(ex)))
            self.flush()

        

################################################################################

                            # Automator

################################################################################


class ProvisionAddHandler(APIHandler, Catalog):

    @web.authenticated
    async def post(self, *args, **kwargs):

        payload = self.get_json_body()
        self.write(payload)
        self.flush()


################################################################################

                            # Workflows

################################################################################


class ExportWorkflowHandler(APIHandler):

    @web.authenticated
    async def post(self, *args, **kwargs):

        payload = self.get_json_body()
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
        template = template_env.get_template('workflow_template.jinja2')
        template.stream(deps_dag=deps_dag, cells=cells, global_params=set(global_params)).dump('workflow.yaml')
        self.flush()
        

