import os
import tornado.web
import requests.adapters
import urllib3
import logging
from urllib.parse import urlencode
from notebook.base.handlers import APIHandler
from requests import RequestException

# customized requests.Session [w/ auto retry]
session = requests.Session()
retry_adapter = requests.adapters.HTTPAdapter(max_retries=urllib3.Retry(total=5, status_forcelist=[500]))
session.mount('http://', retry_adapter)
session.mount('https://', retry_adapter)

logger = logging.getLogger(__name__)


class BackendRelay(APIHandler):
    API_ENDPOINT: str = os.getenv('API_ENDPOINT', 'https://naavre-dev.minikube.test/vre-api-test')
    # API_ENDPOINT: str = 'https://naavre-dev.minikube.test/vre-api-test'
    # API_ENDPOINT: str = 'http://localhost:8000'
    VRE_API_VERIFY_SSL: bool = os.getenv('VRE_API_VERIFY_SSL', 'false').lower() == 'true'

    # login_url = os.getenv('KEYCLOAK_LOGIN_URL', 'https://naavre-dev.minikube.test/auth/realms/vre/protocol/openid-connect/token')

    def __init__(self, application, request):
        super().__init__(application, request)
        self.access_token: str = os.getenv("NAAVRE_API_TOKEN")
        # self.access_token: str = ''
        self.refresh_token: str = ''

    @staticmethod
    def convert_url(rel_url: str) -> str:
        return f'{BackendRelay.API_ENDPOINT}/api/{rel_url[len("/vre/"):]}'

    @staticmethod
    def error_in_json(url: str, status_code: int, error_message: str = 'Unknown error') -> dict[str, any]:
        return {'url': url, 'sta': status_code, 'msg': error_message}

    def get_with_auth(self, url: str):
        return session.get(url, verify=BackendRelay.VRE_API_VERIFY_SSL, headers={'Authorization': f'Token {self.access_token}'})
        # return session.get(url, verify=BackendRelay.VRE_API_VERIFY_SSL, headers={})

    @tornado.web.authenticated
    async def get(self):
        url: str = BackendRelay.convert_url(self.request.uri)
        response = self.get_with_auth(url)
        # if response.status_code == 401 or response.status_code == 403:
        #     try:
        #         logger.debug('Trying to login')
        #         # login_response_body = requests.post(BackendRelay.login_url, headers={'Content-Type': 'application/x-www-form-urlencoded'}, data=urlencode({'client_id': 'myclient', 'grant_type': 'password', 'scope': 'openid', 'username': 'u', 'password': 'u'}), verify=False).json()
        #         response = self.get_with_auth()
        #     except RequestException as e:
        #         err_msg = 'Backend login error'
        #         self.set_status(e.response.status_code)
        #         self.write(self.error_in_json(e.request.url, e.response.status_code, err_msg))
        #         logger.error(err_msg)
        #         return
        if response.status_code == 200:
            return self.write(response.json())
        self.set_status(response.status_code)
        self.write(BackendRelay.error_in_json(url, response.status_code))
