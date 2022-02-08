import json
from unittest import mock

from tornado.escape import to_unicode
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from jupyterlab_vre import ExtractorHandler


class UserAPITest(AsyncHTTPTestCase):
    def get_app(self):
        self.app = Application([('/extractorhandler', ExtractorHandler)],
                                       cookie_secret='asdfasdf')
        return self.app

    def test_user_profile_annoymous(self):
        with mock.patch.object(ExtractorHandler, 'get_secure_cookie') as m:
            m.return_value = 'user_email'
            response = self.fetch('/extractorhandler', method='GET')
        response_body = json.loads(to_unicode(response.body))
        self.assertEqual('Operation not supported.', response_body['title'])