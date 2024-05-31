import os
import tornado.web
import requests.adapters
import urllib3
import logging
from notebook.base.handlers import APIHandler

# customized requests.Session [w/ auto retry]
session = requests.Session()
retry_adapter = requests.adapters.HTTPAdapter(max_retries=urllib3.Retry(total=5, status_forcelist=[500]))
session.mount('http://', retry_adapter)
session.mount('https://', retry_adapter)

logger = logging.getLogger(__name__)


class BackendRelay(APIHandler):
    API_ENDPOINT: str = os.getenv('API_ENDPOINT')
    VRE_API_VERIFY_SSL: bool = os.getenv('VRE_API_VERIFY_SSL', 'false').lower() == 'true'
    NAAVRE_API_TOKEN: str = os.getenv('NAAVRE_API_TOKEN')

    def __init__(self, application, request):
        super().__init__(application, request)

    @staticmethod
    def convert_url(rel_url: str) -> str:
        return f'{BackendRelay.API_ENDPOINT}/api/{rel_url[len("/vre/"):]}'

    @staticmethod
    def error_in_json(url: str, status_code: int, error_message: str = 'Unknown error') -> dict[str, any]:
        return {'url': url, 'sta': status_code, 'msg': error_message}

    def get_with_auth(self, url: str):
        return session.get(url, verify=BackendRelay.VRE_API_VERIFY_SSL, headers={'Authorization': f'Token {BackendRelay.NAAVRE_API_TOKEN}'})

    @tornado.web.authenticated
    async def get(self):
        url: str = BackendRelay.convert_url(self.request.uri)
        response = self.get_with_auth(url)
        if response.status_code == 200:
            return self.write(response.json())
        self.set_status(response.status_code)
        self.write(BackendRelay.error_in_json(url, response.status_code))
