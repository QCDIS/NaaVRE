import copy
import json
from unittest import mock

from tornado.escape import to_unicode
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from jupyterlab_vre import ExtractorHandler, TypesHandler, CellsHandler
from jupyterlab_vre.faircell import Cell
from jupyterlab_vre.storage.catalog import Catalog


class UserAPITest(AsyncHTTPTestCase):



    def get_app(self):
        cell = Cell(
            title               = 'title',
            task_name           = 'title'.lower().replace(' ', '-'),
            original_source     = 'source',
            inputs              = [],
            outputs             = [],
            params              = [],
            confs               = [],
            dependencies        = [],
            container_source    = ""
        )
        Catalog.editor_buffer = copy.deepcopy(cell)
        self.app = Application([('/extractorhandler', ExtractorHandler),
                                ('/typeshandler', TypesHandler),
                                ('/cellshandler', CellsHandler)
                                ],
                                       cookie_secret='asdfasdf')
        return self.app

    # def test_extractorhandler_get(self):
    #     with mock.patch.object(ExtractorHandler, 'get_secure_cookie') as m:
    #         m.return_value = 'cookie'
    #         response = self.fetch('/extractorhandler', method='GET')
    #     response_body = json.loads(to_unicode(response.body))
    #     self.assertEqual('Operation not supported.', response_body['title'])

    # def test_extractorhandler_post(self):
    #     with mock.patch.object(ExtractorHandler, 'get_secure_cookie') as m:
    #         m.return_value = 'cookie'
    #         payload = {'cell_index': 'cell_index', 'notebook': 'notebook'}
    #         response = self.fetch('/extractorhandler', method='POST',body=json.dumps(payload))
    #
    #     response_body = json.loads(to_unicode(response.body))
        # self.assertEqual('Operation not supported.', response_body['title'])

    # def test_typeshandler_post(self):
    #     with mock.patch.object(ExtractorHandler, 'get_secure_cookie') as m:
    #         m.return_value = 'cookie'
    #         payload = {'port': 'port', 'type': 'type'}
    #         response = self.fetch('/typeshandler', method='POST',body=json.dumps(payload))
    #
    #     response_body = json.loads(to_unicode(response.body))
        # self.assertEqual('Operation not supported.', response_body['title'])


    def test_cellshandler_get(self):
        with mock.patch.object(ExtractorHandler, 'get_secure_cookie') as m:
            m.return_value = 'cookie'
            response = self.fetch('/cellshandler', method='GET')
        response_body = json.loads(to_unicode(response.body))
        self.assertEqual('Operation not supported.', response_body['title'])

    def test_cellshandler_post(self):
        with mock.patch.object(ExtractorHandler, 'get_secure_cookie') as m:
            m.return_value = 'cookie'
            payload = {'port': 'port', 'type': 'type'}
            response = self.fetch('/cellshandler', method='POST',body=json.dumps(payload))

        response_body = json.loads(to_unicode(response.body))
        self.assertEqual('Operation not supported.', response_body['title'])