import copy
import json
import os
import traceback
from unittest import mock

import github3
from tornado.escape import to_unicode
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from jupyterlab_vre import ExtractorHandler, TypesHandler, CellsHandler, GithubAuthHandler, ExportWorkflowHandler
from jupyterlab_vre.storage.faircell import Cell
from jupyterlab_vre.storage.catalog import Catalog


def delete_all_cells():
    for cell in Catalog.get_all_cells():
        print(cell)
        Catalog.delete_cell_from_title(cell['title'])


class HandlersAPITest(AsyncHTTPTestCase):

    def get_app(self):
        notebook_path = 'resources/notebooks/test_notebook.ipynb'
        with open(notebook_path, mode="r", encoding="utf-8") as f:
            self.notebook_dict = json.load(f)
        self.app = Application([('/extractorhandler', ExtractorHandler),
                                ('/typeshandler', TypesHandler),
                                ('/cellshandler', CellsHandler),
                                ('/githubauthhandler', GithubAuthHandler),
                                ('/exportworkflowhandler', ExportWorkflowHandler),
                                ],
                               cookie_secret='asdfasdf')
        return self.app

    def test_extractorhandler_get(self):
        with mock.patch.object(ExtractorHandler, 'get_secure_cookie') as m:
            m.return_value = 'cookie'
            response = self.fetch('/extractorhandler', method='GET')
        response_body = json.loads(to_unicode(response.body))
        self.assertEqual('Operation not supported.', response_body['title'])
