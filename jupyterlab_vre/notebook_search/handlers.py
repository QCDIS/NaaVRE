import json
import logging
import os
import time

import requests
from notebook.base.handlers import APIHandler
from tornado import web

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


################################################################################

# Notebook Search

################################################################################

class NotebookSearchHandler(APIHandler):

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
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
        logger.info('hits: ' + str(results))
        self.write(json.dumps(results))
        self.flush()


class NotebookSearchRatingHandler(APIHandler):

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        term = payload['keyword']
        rating = payload['rating']
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
        data = {
            "client_id": 'NaaVRE',
            "timestamp": str(time.time()),
            "event": event,
            "query": term,
            "num_stars": str(rating),
            "annotated_notebook": annotated_notebook,
        }
        try:
            response = requests.post(search_api_endpoint, json=data,
                                     verify=False,
                                     headers={
                                         "Accept": "*/*",
                                         # "Content-Type": "text/json",
                                         "Authorization": "Token " + str(search_api_token)
                                     },
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
