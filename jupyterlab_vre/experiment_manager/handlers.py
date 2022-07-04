import json
from ntpath import join
import yaml
import logging
import os
from typing import List

from jinja2 import Environment, PackageLoader
from jupyterlab_vre.database.cell import Cell
from notebook.base.handlers import APIHandler
import requests
from tornado import web

from jupyterlab_vre.database.database import Catalog
from jupyterlab_vre.services.parser.parser import WorkflowParser

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ExportWorkflowHandler(APIHandler):
    @web.authenticated
    async def post(self, *args, **kwargs):

        payload = self.get_json_body()

        nodes = payload['nodes']
        links = payload['links']

        parser = WorkflowParser(nodes, links)

        cells = parser.get_workflow_cells()
        deps_dag = parser.get_dependencies_dag()

        global_params = []
        for _nid, cell in cells.items():
            global_params.extend(cell['params'])

        registry_credentials = Catalog.get_registry_credentials()

        if not registry_credentials:
            self.set_status(400)
            self.write('Registry credentials are not set!')
            self.write_error('Registry credentials are not set!')
            self.flush()
            return

        image_repo = registry_credentials[0]['url'].split(
            'https://hub.docker.com/u/')[1]
        loader = PackageLoader('jupyterlab_vre', 'templates')
        template_env = Environment(
            loader=loader, trim_blocks=True, lstrip_blocks=True)
        template = template_env.get_template('workflow_template_v2.jinja2')

        template.stream(
            deps_dag=deps_dag,
            cells=cells,
            nodes=nodes,
            global_params=set(global_params),
            image_repo=image_repo
        ).dump('workflow.yaml')

        self.flush()


class ExecuteWorkflowHandler(APIHandler):
    @web.authenticated
    async def post(self, *args, **kwargs):

        payload = self.get_json_body()
        chart = payload['chart']
        params = payload['params']

        API_ENDPOINT = os.getenv('API_ENDPOINT')
        NAAVRE_API_TOKEN = os.getenv('NAAVRE_API_TOKEN')
        VLAB_SLUG = os.getenv('VLAB_SLUG')

        nodes = chart['nodes']
        links = chart['links']

        parser = WorkflowParser(nodes, links)

        cells = parser.get_workflow_cells()
        deps_dag = parser.get_dependencies_dag()

        global_params = []
        for _nid, cell in cells.items():
            global_params.extend(cell['params'])

        registry_credentials = Catalog.get_registry_credentials()

        if not registry_credentials:
            self.set_status(400)
            self.write('Registry credentials are not set!')
            self.write_error('Registry credentials are not set!')
            self.flush()
            return

        image_repo = registry_credentials[0]['url'].split(
            'https://hub.docker.com/u/')[1]
        loader = PackageLoader('jupyterlab_vre', 'templates')
        template_env = Environment(
            loader=loader, trim_blocks=True, lstrip_blocks=True)
        template = template_env.get_template('workflow_template_v2.jinja2')

        template = template.render(
            vlab_slug=VLAB_SLUG,
            deps_dag=deps_dag,
            cells=cells,
            nodes=nodes,
            global_params=params,
            image_repo=image_repo
        )

        workflow_doc = yaml.safe_load(template)

        req_body = {
            "vlab": VLAB_SLUG,
            "workflow_payload": {
                "workflow": workflow_doc
            }
        }

        resp = requests.post(
            f"{API_ENDPOINT}/api/workflows/submit/",
            data=json.dumps(req_body),
            headers={
                'Authorization': f"Bearer {NAAVRE_API_TOKEN}",
                'Content-Type': 'application/json'
            }
        )

        self.write(resp.json())
        self.flush()
