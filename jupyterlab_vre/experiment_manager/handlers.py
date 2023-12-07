import json
import logging
import os
from pathlib import Path

import requests
import yaml
from jinja2 import Environment, PackageLoader
from notebook.base.handlers import APIHandler
from tornado import web

from jupyterlab_vre.database.catalog import Catalog
from jupyterlab_vre.services.parser.parser import WorkflowParser

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def get_workflow_service_account():
    return os.environ.get('ARGO_WF_SPEC_SERVICEACCOUNT', 'default')


def get_workdir_storage_size():
    return os.environ.get('WORKDIR_STORAGE_SIZE', '1')


def write_workflow_to_file(workflow):
    Path('/tmp/workflow_cells/workflows').mkdir(parents=True, exist_ok=True)
    # Generate random file name
    random_file_name = os.urandom(8).hex()
    with open('/tmp/workflow_cells/workflows/' + random_file_name + '.json', 'w') as f:
        f.write(json.dumps(workflow, indent=2))
        f.close()


class LoadWorkflowHandler(APIHandler):

    @web.authenticated
    async def get(self, *args, **kwargs):
        with open('workflow.wf', 'r') as f:
            payload = json.load(f)
        self.write(payload)
        self.flush()


class SaveWorkflowHandler(APIHandler):

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        with open('workflow.wf', 'w') as f:
            json.dump(payload, f)
        self.flush()


class ExportWorkflowHandler(APIHandler):

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        nodes = payload['nodes']
        links = payload['links']

        try:
            parser = WorkflowParser(nodes, links)
        except Exception as e:
            self.set_status(400)
            self.write('Workflow is not valid!')
            self.write_error('Workflow is not valid!')
            self.flush()
            return

        cells = parser.get_workflow_cells()
        deps_dag = parser.get_dependencies_dag()

        global_params = {}
        for _nid, cell in cells.items():
            if cell:
                for param_name in cell['params']:
                    global_params[param_name] = ''

        registry_credentials = Catalog.get_registry_credentials()
        if not registry_credentials:
            self.set_status(400)
            self.write('Registry credentials are not set!')
            self.write_error('Registry credentials are not set!')
            self.flush()
            return

        vlab_slug = os.getenv('VLAB_SLUG')

        image_repo = registry_credentials[0]['url'].split(
            'https://hub.docker.com/u/')[1]
        loader = PackageLoader('jupyterlab_vre', 'templates')
        template_env = Environment(
            loader=loader, trim_blocks=True, lstrip_blocks=True)
        template = template_env.get_template('workflow_template_v2.jinja2')
        if cell:
            if 'JUPYTERHUB_USER' in os.environ:
                workflow_name = 'n-a-a-vre-' + os.environ['JUPYTERHUB_USER'].replace('_', '-').replace('(',
                                                                                                       '-').replace(')',
                                                                                                                    '-').replace(
                    '.', '-').replace('@',
                                      '-at-').strip()

            template.stream(
                vlab_slug=vlab_slug,
                deps_dag=deps_dag,
                cells=cells,
                nodes=nodes,
                global_params=global_params,
                image_repo=image_repo,
                workflow_name=workflow_name,
                workflow_service_account=get_workflow_service_account(),
                workdir_storage_size=get_workdir_storage_size(),
            ).dump('workflow.yaml')
        self.flush()


class ExecuteWorkflowHandler(APIHandler):
    logger = logging.getLogger(__name__)

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        print('Workflow execution payload: ' + json.dumps(payload, indent=2))
        if os.getenv('DEBUG'):
            write_workflow_to_file(payload)
        chart = payload['chart']
        params = payload['params']

        api_endpoint = os.getenv('API_ENDPOINT')
        if not api_endpoint:
            logger.error('NaaVRE API endpoint environment variable "API_ENDPOINT" is not set!')
            self.set_status(400)
            self.write('NaaVRE API endpoint is not set!')
            self.write_error('NaaVRE API endpoint environment variable "API_ENDPOINT" is not set!')
            self.flush()
            return

        naavre_api_token = os.getenv('NAAVRE_API_TOKEN')
        if not naavre_api_token:
            logger.error('NaaVRE API token environment variable "NAAVRE_API_TOKEN" is not set!')
            self.set_status(400)
            self.write('NaaVRE API token is not set!')
            self.write_error('VNaaVRE API token environment variable "NAAVRE_API_TOKEN" is not set!')
            self.flush()
            return

        vlab_slug = os.getenv('VLAB_SLUG')
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

        if 'JUPYTERHUB_USER' in os.environ:
            workflow_name = 'n-a-a-vre-' + os.environ['JUPYTERHUB_USER'].replace('_', '-').replace('(', '-').replace(
                ')', '-').replace('.', '-').replace('@',
                                                    '-at-').strip()
        template = template.render(
            vlab_slug=vlab_slug,
            deps_dag=deps_dag,
            cells=cells,
            nodes=nodes,
            global_params=params,
            image_repo=image_repo,
            workflow_name=workflow_name,
            workflow_service_account=get_workflow_service_account(),
            workdir_storage_size=get_workdir_storage_size(),
        )
        workflow_doc = yaml.safe_load(template)

        req_body = {
            "vlab": vlab_slug,
            "workflow_payload": {
                "workflow": workflow_doc
            }
        }

        try:
            access_token = os.environ['NAAVRE_API_TOKEN']
            if not access_token:
                self.set_status(400)
                self.write('VRE_API_TOKEN is not set!')
                self.write_error('NAAVRE_API_TOKEN is not set!')
                self.flush()
                return
            vre_api_verify_ssl = os.getenv('VRE_API_VERIFY_SSL', 'true')
            logger.info('Workflow submission request: ' + str(json.dumps(req_body, indent=2)))
            print('Workflow submission request: ' + str(json.dumps(req_body, indent=2)))
            session = requests.Session()
            session.verify = vre_api_verify_ssl

            resp = requests.post(
                f"{api_endpoint}/api/workflows/submit/",
                data=json.dumps(req_body),
                headers={
                    'Authorization': f"Token {access_token}",
                    'Content-Type': 'application/json'
                }
            )
            logger.info('Workflow submission response: ' + str(resp.content))
        except Exception as e:
            logger.error('Workflow submission failed: ' + str(e))
            logger.error('api_endpoint: ' + str(api_endpoint))
            logger.error('vre_api_verify_ssl: ' + str(vre_api_verify_ssl))
            self.set_status(400)
            self.write('Workflow submission failed: ' + str(e))
            self.write_error('Workflow submission failed: ' + str(e))
            self.flush()
            return
        if resp.status_code != 200:
            logger.error('Workflow submission failed: ' + str(resp.content))
            logger.error('api_endpoint: ' + str(api_endpoint))
            self.set_status(resp.status_code)
            self.write('Workflow submission failed: ' + str(resp.content))
            self.write_error('Workflow submission failed: ' + str(resp.content))
            self.flush()
            return
        self.write(resp.json())
        self.flush()
