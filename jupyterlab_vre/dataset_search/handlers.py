import json
import logging
import os
import time
from builtins import print
from pathlib import Path

import requests
from notebook.base.handlers import APIHandler
from tornado import web

from jupyterlab_vre.database.catalog import Catalog

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if 'JUPYTERHUB_USER' in os.environ:
    client_id = 'NaaVRE_' + slugify(os.environ['JUPYTERHUB_USER'])


################################################################################

# Dataset Search

################################################################################

class DatasetSearchHandler(APIHandler):

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        keyword = payload['keyword']

        self.check_environment_variables()
        access_token = os.environ['NAAVRE_API_TOKEN']
        api_endpoint = os.getenv('API_ENDPOINT')
        resp = requests.get(
            f"{api_endpoint}/api/dataprods/",
            headers={
                'Authorization': f"Token {access_token}",
                'Content-Type': 'application/json'
            }
        )
        if resp.status_code != 200:
            self.set_status(resp.status_code)
            self.write('Failed to search data: ' + str(resp.content))
            self.flush()
            return
        self.write(json.dumps(resp.json()))
        self.flush()


    def check_environment_variables(self):
        if not os.getenv('API_ENDPOINT'):
            logger.error('NaaVRE API endpoint environment variable "API_ENDPOINT" is not set!')
            self.set_status(400)
            self.write('NaaVRE API endpoint is not set!')
            self.write_error('NaaVRE API endpoint environment variable "API_ENDPOINT" is not set!')
            self.flush()
            return

        if not os.getenv('NAAVRE_API_TOKEN'):
            logger.error('NaaVRE API token environment variable "NAAVRE_API_TOKEN" is not set!')
            self.set_status(400)
            self.write('NaaVRE API token is not set!')
            self.write_error('VNaaVRE API token environment variable "NAAVRE_API_TOKEN" is not set!')
            self.flush()
            return
        if not os.getenv('VLAB_SLUG'):
            logger.error('VL name is not set!')
            self.set_status(400)
            self.write('VL name is not set!')
            self.write_error('VL name environment variable "VLAB_SLUG" is not set!')
            self.flush()
            return
        if not Catalog.get_registry_credentials():
            self.set_status(400)
            self.write('Registry credentials are not set!')
            self.write_error('Registry credentials are not set!')
            self.flush()
            return
class DatasetDownloadHandler(APIHandler):

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        print(payload)
        uuid = payload['uuid']
        dataset_name = payload['title']
        try:
            download_path = Path(Path.home(), 'Downloads', 'Datasets')
            download_response = {'dataset_path': str(Path(download_path, dataset_name))}
            self.write(json.dumps(download_response))
            self.flush()
        except Exception as ex:
            self.set_status(500)
            self.write(str(ex))
            self.write_error(str(ex))
            self.flush()
            return