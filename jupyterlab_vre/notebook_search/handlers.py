import json
import logging
import os
import time
from builtins import print

import requests
from notebook.base.handlers import APIHandler
from tornado import web

from pathlib import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


################################################################################

# Notebook Search

################################################################################

class NotebookSearchHandler(APIHandler):

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        print(json.dumps(payload))
        term = payload['keyword']
        search_api_endpoint = os.getenv('SEARCH_API_ENDPOINT')
        search_api_token = os.getenv('SEARCH_API_TOKEN')
        if not search_api_endpoint:
            logger.error('Environment variable: SEARCH_API_ENDPOINT not set')
            self.set_status(500)
            self.write('Environment variable: SEARCH_API_ENDPOINT not set')
            self.write_error('Environment variable: SEARCH_API_ENDPOINT not set')
            self.flush()
            return
        if not search_api_token:
            logger.error('Environment variable: SEARCH_API_TOKEN not set')
            self.set_status(500)
            self.write('Environment variable: SEARCH_API_TOKEN not set')
            self.write_error('Environment variable: SEARCH_API_TOKEN not set')
            self.flush()
            return
        params = {
            "page": "1",
            "query": term,
            "filter": "",
            "facet": "",
        }
        try:
            response = requests.get(search_api_endpoint + 'notebook_search', params=params,
                                    verify=False,
                                    headers={
                                        "Accept": "*/*",
                                        # "Content-Type": "text/json",
                                        "Authorization": "Token " + str(search_api_token)
                                    },
                                    timeout=4)
            hits = response.json()
        except Exception as ex:
            logger.error('Failed to get results from: ' + search_api_endpoint + ' ' + str(ex))
            self.set_status(500)
            self.write('Failed to get results from: ' + search_api_endpoint + ' ' + str(ex))
            self.write_error('Failed to get results from: ' + search_api_endpoint + ' ' + str(ex))
            self.flush()
            return
        if not hits or 'results' not in hits:
            results = ['No results found']
        else:
            results = hits['results']
        for res in results:
            res['rating'] = 1
        logger.info('hits: ' + str(results))
        self.write(json.dumps(results))
        self.flush()


class NotebookSearchRatingHandler(APIHandler):

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        print(json.dumps(payload))
        term = payload['keyword']
        notebook = payload['notebook']
        search_api_endpoint = os.getenv('SEARCH_API_ENDPOINT')
        search_api_token = os.getenv('SEARCH_API_TOKEN')
        if not search_api_endpoint:
            logger.error('Environment variable: SEARCH_API_ENDPOINT not set')
            self.set_status(500)
            self.write('Environment variable: SEARCH_API_ENDPOINT not set')
            self.write_error('Environment variable: SEARCH_API_ENDPOINT not set')
            self.flush()
            return
        if not search_api_token:
            logger.error('Environment variable: SEARCH_API_TOKEN not set')
            self.set_status(500)
            self.write('Environment variable: SEARCH_API_TOKEN not set')
            self.write_error('Environment variable: SEARCH_API_TOKEN not set')
            self.flush()
            return
        event = "relevancy_feedback"
        annotated_notebook = {}
        for attr in ['docid', 'name', 'source', 'html_url', 'description']:
            annotated_notebook[attr] = notebook[attr]
        data = {
            "client_id": 'NaaVRE',
            "timestamp": str(time.time()),
            "event": event,
            "query": term,
            "num_stars": str(notebook['rating']),
            "annotated_notebook": annotated_notebook,
        }
        try:
            api_config = {'verify': False, 'headers': {'Authorization': 'Token ' + str(search_api_token)}}
            response = requests.post(search_api_endpoint, json=data,
                                     **api_config,
                                     timeout=4)
            feedback = response.json()
        except Exception as ex:
            logger.error('Failed to send rating to: ' + search_api_endpoint + ' ' + str(ex))
            self.set_status(500)
            self.write('Failed to send rating to: ' + search_api_endpoint + ' ' + str(ex))
            self.write_error('Failed to send rating to: ' + search_api_endpoint + ' ' + str(ex))
            self.flush()
            return

        self.flush()


class NotebookDownloadHandler(APIHandler):

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        docid = payload['docid']
        notebook_name = payload['notebook_name']+'.ipynb'
        search_api_endpoint = os.getenv('SEARCH_API_ENDPOINT')
        search_api_token = os.getenv('SEARCH_API_TOKEN')
        if not search_api_endpoint:
            logger.error('Environment variable: SEARCH_API_ENDPOINT not set')
            self.set_status(500)
            self.write('Environment variable: SEARCH_API_ENDPOINT not set')
            self.write_error('Environment variable: SEARCH_API_ENDPOINT not set')
            self.flush()
            return
        if not search_api_token:
            logger.error('Environment variable: SEARCH_API_TOKEN not set')
            self.set_status(500)
            self.write('Environment variable: SEARCH_API_TOKEN not set')
            self.write_error('Environment variable: SEARCH_API_TOKEN not set')
            self.flush()
            return
        params = {
            "docid": docid,
        }
        try:
            response = requests.get(search_api_endpoint + 'notebook_download', params=params,
                                    verify=False,
                                    headers={
                                        "Accept": "*/*",
                                        # "Content-Type": "text/json",
                                        "Authorization": "Token " + str(search_api_token)
                                    },
                                    timeout=4)
            results = response.json()
        except Exception as ex:
            logger.error('Failed to get results from: ' + search_api_endpoint + ' ' + str(ex))
            self.set_status(500)
            self.write('Failed to get results from: ' + search_api_endpoint + ' ' + str(ex))
            self.write_error('Failed to get results from: ' + search_api_endpoint + ' ' + str(ex))
            self.flush()
            return
        notebook_source_file = results['notebook_source_file']
        notebook = json.loads(notebook_source_file)
        download_path = Path(Path.home(), 'Downloads', 'Notebooks')
        if not os.path.exists(download_path):
            os.makedirs(download_path)

        with open(Path(download_path, notebook_name), 'w') as outfile:
            json.dump(notebook, outfile)

        download_response = {'notebook_path': str(Path(download_path, notebook_name))}
        self.write(json.dumps(download_response))
        self.flush()
