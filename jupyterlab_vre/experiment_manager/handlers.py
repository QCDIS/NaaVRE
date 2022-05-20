import copy
import json
import uuid
from jupyterlab_vre.services.parser.parser import WorkflowParser
from jinja2 import Environment, PackageLoader

import nbformat as nb
from jupyterlab_vre.converter.converter import ConverterReactFlowChart
from jupyterlab_vre.extractor.extractor import Extractor
from jupyterlab_vre.storage.catalog import Catalog
from jupyterlab_vre.storage.faircell import Cell
from notebook.base.handlers import APIHandler
from tornado import web


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