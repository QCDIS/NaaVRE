import json
import logging

from jinja2 import Environment, PackageLoader
from notebook.base.handlers import APIHandler
from tornado import web

from jupyterlab_vre.database.database import Catalog
from jupyterlab_vre.services.parser.parser import WorkflowParser

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ExportWorkflowHandler(APIHandler):
    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        global_params = []

        nodes = payload['nodes']
        links = payload['links']
        try:
            parser = WorkflowParser(nodes, links)
        except Exception as ex:
            logger.error(str(ex) + ' payload: ' + json.dumps(payload))
            self.set_status(400)
            self.write(str(ex))
            self.write_error(str(ex))
            self.flush()
            return

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
        image_repo = registry_credentials[0]['url'].split('https://hub.docker.com/u/')[1]
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
