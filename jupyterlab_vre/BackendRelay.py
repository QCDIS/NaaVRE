import json
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
    COMMON_HEADERS = {
        'Authorization': f'Token {NAAVRE_API_TOKEN}',
        "Content-Type": "application/json",
    }

    def __init__(self, application, request):
        super().__init__(application, request)

    @staticmethod
    def convert_url(rel_url: str) -> str:
        return f'{BackendRelay.API_ENDPOINT}/api/{rel_url[len("/vre/"):]}'

    @staticmethod
    def error_in_json(url: str, status_code: int, error_message: str = 'Unknown error') -> dict[str, any]:
        return {'url': url, 'sta': status_code, 'msg': error_message}

    def send_with_auth(self, url: str, method='GET', body: any = None):
        logger.warning(f'<debug> {url}')
        match method:
            case 'GET':
                return session.get(url, verify=BackendRelay.VRE_API_VERIFY_SSL, headers=BackendRelay.COMMON_HEADERS)
            case 'POST':
                return session.post(url, verify=BackendRelay.VRE_API_VERIFY_SSL, headers=BackendRelay.COMMON_HEADERS, data=body)

    def common_response_handler(self, response: requests.Response):
        if response.status_code == 200:
            ret = response.json()
            if isinstance(ret, list):
                ret = json.dumps(ret)
            return self.write(ret)
        self.set_status(response.status_code)
        self.write(BackendRelay.error_in_json(response.url, response.status_code, response.text))

    @tornado.web.authenticated
    async def get(self):
        url: str = BackendRelay.convert_url(self.request.uri)
        response = self.send_with_auth(url)
        return self.common_response_handler(response)

    @tornado.web.authenticated
    async def post(self):
        url: str = BackendRelay.convert_url(self.request.uri)
        response = self.send_with_auth(url, 'POST', self.request.body)
        return self.common_response_handler(response)
