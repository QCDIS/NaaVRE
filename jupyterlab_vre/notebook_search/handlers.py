import json
import logging
import os
import time
from builtins import print

import requests
from notebook.base.handlers import APIHandler
from tornado import web
from jupyterlab_vre.database.database import Catalog
from pathlib import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if 'JUPYTERHUB_USER' in os.environ:
    client_id = 'NaaVRE_' + os.environ['JUPYTERHUB_USER'].replace('_', '-').replace('(', '-').replace(')', '-').replace('.', '-').replace('@',
                                                                                                     '_at_').strip()


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

        event = 'notebook_search'
        data = {
            'client_id': client_id,
            'timestamp': str(time.time()),
            'event': event,
            'query': term,
        }
        try:
            results = []
            for i in range(1, 10):
                params = {
                    'page': str(i),
                    'query': term,
                    'filter': '',
                    'facet': '',
                }

                api_config = {'verify': False, 'headers': {'Authorization': 'Token ' + str(search_api_token)}}
                response = requests.post(search_api_endpoint + 'notebook_search', params=params, json=data,
                                         **api_config,
                                         timeout=10)

                if 'results' in response.json():
                    results += response.json()['results']
                else:
                    break
        except Exception as ex:
            logger.error('Failed to get results from: ' + search_api_endpoint + ' ' + str(ex))
            self.set_status(500)
            self.write('Failed to get results from: ' + search_api_endpoint + ' ' + str(ex))
            self.write_error('Failed to get results from: ' + search_api_endpoint + ' ' + str(ex))
            self.flush()
            return
        search_entry = {'query': term, 'results': results, 'timestamp': time.time()}
        Catalog.add_search_enty(search_entry)
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
        event = 'relevancy_feedback'
        annotated_notebook = {}
        for attr in ['docid', 'name', 'source', 'html_url', 'description']:
            annotated_notebook[attr] = notebook[attr]
        data = {
            'client_id': client_id,
            'timestamp': str(time.time()),
            'event': event,
            'query': term,
            'num_stars': str(notebook['rating']),
            'annotated_notebook': annotated_notebook,
        }
        try:
            api_config = {'verify': False, 'headers': {'Authorization': 'Token ' + str(search_api_token)}}
            response = requests.post(search_api_endpoint + 'relevancy_feedback/', json=data, **api_config)
            if response.status_code != 201:
                raise Exception('Failed code: ' + str(response.status_code))
            feedback = response.json()
            logger.debug('feedback: ' + str(feedback))
        except Exception as ex:
            logger.error('Failed to send rating to: ' + search_api_endpoint + ' ' + str(ex))
            self.set_status(500)
            self.write('Failed to send rating to: ' + search_api_endpoint + ' ' + str(ex))
            self.write_error('Failed to send rating to: ' + search_api_endpoint + ' ' + str(ex))
            self.flush()
            return

        self.flush()


def get_notebook_source_content(doc_id=None):
    search_api_endpoint = os.getenv('SEARCH_API_ENDPOINT')
    search_api_token = os.getenv('SEARCH_API_TOKEN')
    if not search_api_endpoint:
        logger.error('Environment variable: SEARCH_API_ENDPOINT not set')
        raise Exception('Environment variable: SEARCH_API_ENDPOINT not set')
    if not search_api_token:
        logger.error('Environment variable: SEARCH_API_TOKEN not set')
        raise Exception('Environment variable: SEARCH_API_TOKEN not set')
    params = {
        'docid': doc_id,
    }
    try:
        response = requests.get(search_api_endpoint + 'notebook_download', params=params,
                                verify=False,
                                headers={
                                    'Accept': '*/*',
                                    # 'Content-Type': 'text/json',
                                    'Authorization': 'Token ' + str(search_api_token)
                                },
                                timeout=4)
        results = response.json()
    except Exception as ex:
        logger.error('Failed to get results from: ' + search_api_endpoint + ' ' + str(ex))
        raise Exception('Failed to get results from: ' + search_api_endpoint + ' ' + str(ex))

    notebook_source_file = results['notebook_source_file']
    return notebook_source_file


class NotebookDownloadHandler(APIHandler):

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        docid = payload['docid']
        notebook_name = payload['notebook_name'] + '.ipynb'
        try:
            notebook_source_file = get_notebook_source_content(doc_id=docid)
            notebook = json.loads(notebook_source_file)
            download_path = Path(Path.home(), 'Downloads', 'Notebooks')
            if not os.path.exists(download_path):
                os.makedirs(download_path)

            with open(Path(download_path, notebook_name), 'w') as outfile:
                json.dump(notebook, outfile)

            download_response = {'notebook_path': str(Path(download_path, notebook_name))}
            self.write(json.dumps(download_response))
            self.flush()
        except Exception as ex:
            self.set_status(500)
            self.write(str(ex))
            self.write_error(str(ex))
            self.flush()
            return


class NotebookSourceHandler(APIHandler):

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        docid = payload['docid']
        print('Get source for: ' + docid)
        try:
            notebook_source_file = get_notebook_source_content(doc_id=docid)
            response = {'notebook_source': json.loads(notebook_source_file)}
            print(response)
            self.write(response)
            self.flush()
        except Exception as ex:
            self.set_status(500)
            self.write(str(ex))
            self.write_error(str(ex))
            self.flush()
            return


class NotebookSeachHistoryHandler(APIHandler):
    @web.authenticated
    async def get(self, *args, **kwargs):
        payload = self.get_json_body()
        print(json.dumps(payload))
        msg_json = dict(title='Operation not supported.')
        self.write(msg_json)
        await self.flush()
