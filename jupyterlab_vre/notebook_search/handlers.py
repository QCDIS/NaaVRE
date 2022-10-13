import json
import logging
import os
from _curses_panel import panel

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
        logger.info('payload: ' + str(payload))
        term = payload['keyword']
        search_api_endpoint = os.getenv('SEARCH_API_ENDPOINT')
        search_api_token = os.getenv('SEARCH_API_TOKEN')
        if not search_api_endpoint:
            search_api_endpoint = 'http://145.100.135.119/api/notebook_search/'
        if not search_api_token:
            search_api_token = 'b30bd18ea01f5a45e217b03682f70ce6ae14c293'
        logger.info('search_api_endpoint: ' + str(search_api_endpoint))
        response = requests.get(
            search_api_endpoint,
            params={
                "page": "1",
                "term": term,
                "filter": "",
                "facet": ""
            },
            verify=False,
            headers={
                "Accept": "*/*",
                "Content-Type": "text/json",
                "Authorization": "Token " + str(search_api_token)
            }
        )
        hits = response.text
        logger.info('hits: ' + str(hits))
        self.write(hits)
        self.flush()
