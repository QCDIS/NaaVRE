import copy
import json
import os
from unittest import mock

from tornado.escape import to_unicode
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from jupyterlab_vre import ExtractorHandler, TypesHandler, CellsHandler, ExportWorkflowHandler
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
                                ],
                               cookie_secret='asdfasdf')
        return self.app

    def test_export_workflow_handler(self):
        with mock.patch.object(ExtractorHandler, 'get_secure_cookie') as m:
            m.return_value = 'cookie'
            workflow_path = os.path.join(base_path, 'workflows/get_files.json')
            with open(workflow_path, 'r') as read_file:
                payload = json.load(read_file)
            response = self.fetch('/exportworkflowhandler', method='POST', body=json.dumps(payload))

    def test_load_module_names_mapping(self):
        load_module_names_mapping()


    def test_extractor_handler_MULTIPLY(self):
        with mock.patch.object(ExtractorHandler, 'get_secure_cookie') as m:
            m.return_value = 'cookie'
            workflow_path = os.path.join(base_path, 'notebooks/MULTIPLY_framework_2.json')
            with open(workflow_path, 'r') as read_file:
                payload = json.load(read_file)
            response = self.fetch('/exportworkflowhandler', method='POST', body=json.dumps(payload))
