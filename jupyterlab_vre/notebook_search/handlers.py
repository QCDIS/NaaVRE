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
        term = payload['keyword']
        search_api_endpoint = os.getenv('SEARCH_API_ENDPOINT')
        search_api_token = os.getenv('SEARCH_API_TOKEN')
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
                "Authorization": "Token "+search_api_token
            }
        )
        hits = response.text
        self.write(hits)
        self.flush()
