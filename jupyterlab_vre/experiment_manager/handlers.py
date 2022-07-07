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
    logger = logging.getLogger(__name__)

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
    logger = logging.getLogger(__name__)

    @web.authenticated
    async def post(self, *args, **kwargs):

        payload = self.get_json_body()
        chart = payload['chart']
        params = payload['params']

        api_endpoint = os.getenv('API_ENDPOINT')
        logger.debug('API_ENDPOINT: ' + api_endpoint)
        print('API_ENDPOINT: '+str(api_endpoint))
        if not api_endpoint:
            logger.error('NaaVRE API endpoint environment variable "API_ENDPOINT" is not set!')
            self.set_status(400)
            self.write('NaaVRE API endpoint is not set!')
            self.write_error('NaaVRE API endpoint environment variable "API_ENDPOINT" is not set!')
            self.flush()
            return

        naavre_api_token = os.getenv('NAAVRE_API_TOKEN')
        print('API_ENDPOINT: ' + str(naavre_api_token))
        if not naavre_api_token:
            logger.error('NaaVRE API token environment variable "NAAVRE_API_TOKEN" is not set!')
            self.set_status(400)
            self.write('NaaVRE API token is not set!')
            self.write_error('VNaaVRE API token environment variable "NAAVRE_API_TOKEN" is not set!')
            self.flush()
            return

        vlab_slug = os.getenv('VLAB_SLUG')
        print('vlab_slug: ' + vlab_slug)
        if not vlab_slug:
            logger.error('VL name is not set!')
            self.set_status(400)
            self.write('VL name is not set!')
            self.write_error('VL name environment variable "VLAB_SLUG" is not set!')
            self.flush()
            return

        nodes = chart['nodes']
        links = chart['links']

        parser = WorkflowParser(nodes, links)

        cells = parser.get_workflow_cells()
        deps_dag = parser.get_dependencies_dag()

        global_params = []
        for _nid, cell in cells.items():
            global_params.extend(cell['params'])

        registry_credentials = Catalog.get_registry_credentials()
        print('l22')
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

        print('l137')

        template = template.render(
            vlab_slug=vlab_slug,
            deps_dag=deps_dag,
            cells=cells,
            nodes=nodes,
            global_params=params,
            image_repo=image_repo
        )
        print('l145')
        workflow_doc = yaml.safe_load(template)
        print('workflow_doc: ' + str(workflow_doc))

        req_body = {
            "vlab": vlab_slug,
            "workflow_payload": {
                "workflow": workflow_doc
            }
        }
        print('API request body: ' + (str(req_body)))
        logger.debug('API request body: ' + (str(req_body)))

        print('l158')
        logger.debug('api_endpoint: ' + (str(api_endpoint)))
        print('api_endpoint: ' + (str(api_endpoint)))
        print('-*-----------------------------------------------------------')

        resp = requests.post(
            f"{api_endpoint}/api/workflows/submit/",
            data=json.dumps(req_body),
            headers={
                'Authorization': f"Bearer {naavre_api_token}",
                'Content-Type': 'application/json'
            }
        )

        print('-*-----------------------------------------------------------')
        logger.debug('API response: ' + (str(resp)))
        print('API response: ' + (str(resp)))
        print('-*-----------------------------------------------------------')

        self.write(resp.json())
        self.flush()