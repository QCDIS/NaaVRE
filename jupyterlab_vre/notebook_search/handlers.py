import json
import logging

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
        response = requests.get(
            'http://145.100.135.119/api/notebook_search/',
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
                "Authorization": "Token b30bd18ea01f5a45e217b03682f70ce6ae14c293"
            }
        )
        hits = response.text
        json_object = json.loads(hits)
        print(hits)
        self.write(hits)
        self.flush()
