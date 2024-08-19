import base64
import json
import logging
import os
from pathlib import Path
from time import sleep

import requests
import yaml
from jinja2 import Environment, PackageLoader
from jupyterlab_vre.component_containerizer.handlers import git_hash
from notebook.base.handlers import APIHandler
from slugify import slugify
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

def write_argo_workflow_to_file(workflow):
    Path('/tmp/workflow_cells/argo_workflows').mkdir(parents=True, exist_ok=True)
    # Generate random file name
    random_file_name = os.urandom(8).hex()
    with open('/tmp/workflow_cells/argo_workflows/' + random_file_name + '.yaml', 'w') as f:
        f.write(yaml.dump(workflow))
        f.close()


def write_argo_workflow_to_file(workflow):
    Path('/tmp/workflow_cells/argo_workflows').mkdir(parents=True, exist_ok=True)
    # Generate random file name
    random_file_name = os.urandom(8).hex()
    with open('/tmp/workflow_cells/argo_workflows/' + random_file_name + '.yaml', 'w') as f:
        f.write(yaml.dump(workflow))
        f.close()


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

        image_repo = registry_credentials[0]['url']
        loader = PackageLoader('jupyterlab_vre', 'templates')
        template_env = Environment(
            loader=loader, trim_blocks=True, lstrip_blocks=True)
        template = template_env.get_template('workflow_template_v2.jinja2')
        if cell:
            if 'JUPYTERHUB_USER' in os.environ:
                workflow_name = 'n-a-a-vre-' + slugify(os.environ['JUPYTERHUB_USER'])

            template.stream(
                vlab_slug=vlab_slug,
                deps_dag=deps_dag,
                cells=cells,
                nodes=nodes,
                global_params=global_params,
                k8s_secret_name='ext-workflow-secret',
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
        if os.getenv('DEBUG'):
            write_workflow_to_file(payload)
        chart = payload['chart']
        params = payload['params']
        self.check_environment_variables()

        api_endpoint = os.getenv('API_ENDPOINT')
        vlab_slug = os.getenv('VLAB_SLUG')
        nodes = chart['nodes']
        links = chart['links']

        parser = WorkflowParser(nodes, links)

        cells = parser.get_workflow_cells()
        deps_dag = parser.get_dependencies_dag()

        global_params = []
        for _nid, cell in cells.items():
            global_params.extend(cell['params'])

        try:
            secrets = payload.get('secrets')
            if secrets:
                k8s_secret_name = self.add_secrets_to_k8s(secrets)
            else:
                k8s_secret_name = None
        except Exception as e:
            logger.error(f"Secret creation failed: {e}")
            logger.error(f"api_endpoint: {api_endpoint}")
            logger.error(f"vre_api_verify_ssl: {self.vre_api_verify_ssl}")
            self.set_status(400)
            self.write(f"Secret creation failed: {e}")
            self.write_error(f"Secret creation failed: {e}")
            self.flush()
            return

        registry_credentials = Catalog.get_registry_credentials()

        image_repo = registry_credentials[0]['url']
        loader = PackageLoader('jupyterlab_vre', 'templates')
        template_env = Environment(
            loader=loader, trim_blocks=True, lstrip_blocks=True)
        template = template_env.get_template('workflow_template_v2.jinja2')
        workflow_name = 'n-a-a-vre'
        if 'JUPYTERHUB_USER' in os.environ:
            workflow_name = 'n-a-a-vre-' + slugify(os.environ['JUPYTERHUB_USER'])
        for cell_id in cells:
            if 'image_version' not in cells[cell_id]:
                logger.error(f"Image version is not set for cell {cells[cell_id]['title']}")
                self.set_status(400)
                self.write(f"Image version is not set for cell {cell_id}")
                self.write_error(f"Image version is not set for cell {cell_id}")
                self.flush()

        template = template.render(
            vlab_slug=vlab_slug,
            deps_dag=deps_dag,
            cells=cells,
            nodes=nodes,
            global_params=params,
            k8s_secret_name=k8s_secret_name,
            image_repo=image_repo,
            workflow_name=workflow_name,
            workflow_service_account=get_workflow_service_account(),
            workdir_storage_size=get_workdir_storage_size(),
        )
        workflow_doc = yaml.safe_load(template)
        if os.getenv('DEBUG'):
            write_argo_workflow_to_file(workflow_doc)
        req_body = {
            "vlab": vlab_slug,
            "workflow_payload": {
                "workflow": workflow_doc
            }
        }

        try:
            access_token = os.environ['NAAVRE_API_TOKEN']
            logger.info('Workflow submission request: ' + str(json.dumps(req_body, indent=2)))

            resp = requests.post(
                f"{api_endpoint}/api/workflows/submit/",
                verify=self.vre_api_verify_ssl,
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
            logger.error('vre_api_verify_ssl: ' + str(self.vre_api_verify_ssl))
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

    @web.authenticated
    async def get(self, *args, **kwargs):
        workflow_id = self.get_argument('workflow_id', default=None)
        self.check_environment_variables()
        api_endpoint = os.getenv('API_ENDPOINT')
        access_token = os.environ['NAAVRE_API_TOKEN']
        # This is a bug. If we don't do this, the workflow status is not updated.
        resp = requests.get(
            f"{api_endpoint}/api/workflows/",
            verify=self.vre_api_verify_ssl,
            headers={
                'Authorization': f"Token {access_token}",
                'Content-Type': 'application/json'
            }
        )
        wf_list = resp.json()
        for wf in wf_list:
            if wf['argo_id'] == workflow_id:
                self.write(wf)
                self.set_status(resp.status_code)
                self.flush()
                return
        sleep(0.3)
        resp = requests.get(
            f"{api_endpoint}/api/workflows/{workflow_id}/",
            verify=self.vre_api_verify_ssl,
            headers={
                'Authorization': f"Token {access_token}",
                'Content-Type': 'application/json'
            }
        )
        self.write(resp.json())
        self.set_status(resp.status_code)
        self.flush()

    @property
    def vre_api_verify_ssl(self):
        return os.getenv('VRE_API_VERIFY_SSL', 'true').lower() == 'true'

    def add_secrets_to_k8s(self, secrets):
        self.check_environment_variables()
        api_endpoint = os.getenv('API_ENDPOINT')
        access_token = os.getenv('NAAVRE_API_TOKEN')
        body = {
            k: base64.b64encode(v.encode()).decode()
            for k, v in secrets.items()
            }
        resp = requests.post(
            f"{api_endpoint}/api/workflows/create_secret/",
            verify=self.vre_api_verify_ssl,
            headers={
                'Authorization': f"Token {access_token}",
                'Content-Type': 'application/json'
                },
            data=json.dumps(body),
            )
        resp.raise_for_status()
        secret_name = resp.json()['secretName']
        return secret_name

    def check_environment_variables(self):
        if not os.getenv('API_ENDPOINT'):
            logger.error('NaaVRE API endpoint environment variable "API_ENDPOINT" is not set!')
            self.set_status(400)
            self.write('NaaVRE API endpoint is not set!')
            self.write_error('NaaVRE API endpoint environment variable "API_ENDPOINT" is not set!')
            self.flush()
            return

        if not os.getenv('NAAVRE_API_TOKEN'):
            logger.error('NaaVRE API token environment variable "NAAVRE_API_TOKEN" is not set!')
            self.set_status(400)
            self.write('NaaVRE API token is not set!')
            self.write_error('VNaaVRE API token environment variable "NAAVRE_API_TOKEN" is not set!')
            self.flush()
            return
        if not os.getenv('VLAB_SLUG'):
            logger.error('VL name is not set!')
            self.set_status(400)
            self.write('VL name is not set!')
            self.write_error('VL name environment variable "VLAB_SLUG" is not set!')
            self.flush()
            return
        if not Catalog.get_registry_credentials():
            self.set_status(400)
            self.write('Registry credentials are not set!')
            self.write_error('Registry credentials are not set!')
            self.flush()
            return
