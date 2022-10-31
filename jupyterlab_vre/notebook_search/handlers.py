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

        response = requests.get(search_api_endpoint+'notebook_search', params=params,
                                verify=False,
                                headers={
                                    "Accept": "*/*",
                                    # "Content-Type": "text/json",
                                    "Authorization": "Token " + str(search_api_token)
                                }
                                )
        hits = response.json()
        if 'results' not in hits:
            results = ['No results found']
        else:
            results = hits['results']
        logger.info('hits: ' + str(results))
        self.write(json.dumps(results))
        self.flush()
