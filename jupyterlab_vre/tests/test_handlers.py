import copy
import json
import os
from unittest import mock

from jinja2 import PackageLoader, Environment
from tornado.escape import to_unicode
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from jupyterlab_vre import ExtractorHandler, TypesHandler, CellsHandler, ExportWorkflowHandler, ExecuteWorkflowHandler
from jupyterlab_vre.component_containerizer.handlers import map_dependencies
from jupyterlab_vre.database.cell import Cell
from jupyterlab_vre.database.database import Catalog
from jupyterlab_vre.handlers import load_module_names_mapping

if os.path.exists('resources'):
    base_path = 'resources'
elif os.path.exists('jupyterlab_vre/tests/resources/'):
    base_path = 'jupyterlab_vre/tests/resources/'


def delete_all_cells():
    for cell in Catalog.get_all_cells():
        print(cell)
        Catalog.delete_cell_from_title(cell['title'])


class HandlersAPITest(AsyncHTTPTestCase):

    def get_app(self):
        notebook_path = os.path.join(base_path, 'notebooks/test_notebook.ipynb')
        with open(notebook_path, mode='r', encoding='utf-8') as f:
            self.notebook_dict = json.load(f)
        self.app = Application([('/extractorhandler', ExtractorHandler),
                                ('/typeshandler', TypesHandler),
                                ('/cellshandler', CellsHandler),
                                ('/exportworkflowhandler', ExportWorkflowHandler),
                                ('/executeworkflowhandler', ExecuteWorkflowHandler),
                                ],
                               cookie_secret='asdfasdf')
        return self.app

    def test_export_workflow_handler(self):
        with mock.patch.object(ExtractorHandler, 'get_secure_cookie') as m:
            m.return_value = 'cookie'
            workflow_path = os.path.join(base_path, 'workflows/splitter.json')
            with open(workflow_path, 'r') as read_file:
                payload = json.load(read_file)
            # response = self.fetch('/exportworkflowhandler', method='POST', body=json.dumps(payload))

    def test_load_module_names_mapping(self):
        load_module_names_mapping()

    def test_map_dependencies(self):
        dependencies = [{'name': 'pathlib', 'asname': None, 'module': ''},
                        {'name': 'numpy', 'asname': 'np', 'module': ''},
                        {'name': 'laspy', 'asname': None, 'module': ''},
                        {'name': 'Client', 'asname': None, 'module': 'webdav3.client'},
                        {'name': 'os', 'asname': None, 'module': ''},
                        {'name': 'get_wdclient', 'asname': None, 'module': 'laserfarm.remote_utils'},
                        {'name': 'pathlib', 'asname': None, 'module': ''},
                        {'name': 'list_remote', 'asname': None, 'module': 'laserfarm.remote_utils'}]
        set_conda_deps, set_pip_deps = map_dependencies(dependencies=dependencies)
        loader = PackageLoader('jupyterlab_vre', 'templates')
        template_env = Environment(
            loader=loader, trim_blocks=True, lstrip_blocks=True)
        template_conda = template_env.get_template('conda_env_template.jinja2')
        template_conda.stream(base_image='cell.base_image', conda_deps=list(set_conda_deps),
                              pip_deps=list(set_pip_deps)).dump('test_env.yaml')