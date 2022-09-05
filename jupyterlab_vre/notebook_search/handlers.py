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
        keyword = payload['keyword']
        response = requests.post(
            'https://search.envri.eu/KB_notebookSearch/searchNotebooks',
            json={
                "page": "1",
                "keywords": keyword,
                "filter": "",
                "facet": ""
            },
            verify=False,
            headers={
                "Accept": "*/*",
                "Content-Type": "text/plain",
                "Authorization": "Token 34d13602ed292f48b1465d38b35d9b9baddd41e1"
            }
        )

        hits = response.json()['hits']
        self.write(hits)
        self.flush()
