import copy
import json
import os
import traceback
from unittest import mock

import github3
from tornado.escape import to_unicode
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from jupyterlab_vre import ExtractorHandler, TypesHandler, CellsHandler, GithubAuthHandler
from jupyterlab_vre.faircell import Cell
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
                                ('/githubauthhandler', GithubAuthHandler)
                                ],
                               cookie_secret='asdfasdf')
        return self.app

    def test_extractorhandler_get(self):
        with mock.patch.object(ExtractorHandler, 'get_secure_cookie') as m:
            m.return_value = 'cookie'
            response = self.fetch('/extractorhandler', method='GET')
        response_body = json.loads(to_unicode(response.body))
        self.assertEqual('Operation not supported.', response_body['title'])

    def add_cell(self, cell_index=None):
        with mock.patch.object(ExtractorHandler, 'get_secure_cookie') as m:
            m.return_value = 'cookie'
            if cell_index is not None:
                payload = {'notebook': self.notebook_dict, 'cell_index': cell_index}
            else:
                payload = {'notebook': self.notebook_dict, 'cell_index': 0}
            response = self.fetch('/extractorhandler', method='POST', body=json.dumps(payload))
        response_body = json.loads(to_unicode(response.body))
        self.assertNotEqual(response_body, None)
        self.assertNotEqual(response_body['node_id'], None)
        self.assertNotEqual(response_body['chart'], None)
        self.assertNotEqual(response_body['deps'], None)

    def add_git_token(self, git_token):
        with mock.patch.object(ExtractorHandler, 'get_secure_cookie') as m:
            m.return_value = 'cookie'
            payload = {'github-auth-token': git_token}
            response = self.fetch('/githubauthhandler', method='POST', body=json.dumps(payload))
        # response_body = json.loads(to_unicode(response.body))
        # self.assertNotEqual(response_body, None)

    def test_cellshandler_post(self):
        cell_index = 3
        git_token = 'test_token'
        self.add_cell(cell_index=cell_index)
        # self.add_git_token(git_token=git_token)

        with mock.patch.object(ExtractorHandler, 'get_secure_cookie') as m:
            m.return_value = 'cookie'
            payload = {'port': 'port', 'type': 'type'}
            response = self.fetch('/cellshandler', method='POST', body=json.dumps(payload))

        # delete_all_cells()
        response_body = json.loads(to_unicode(response.body))
        self.assertNotEqual(response_body, None)


