import json
import logging
import os
import time
from builtins import print
from pathlib import Path

import uuid
import datetime
import websocket
import requests
from notebook.base.handlers import APIHandler
from slugify import slugify
from tornado import web

from jupyterlab_vre.database.catalog import Catalog

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if 'JUPYTERHUB_USER' in os.environ:
    client_id = 'NaaVRE_' + slugify(os.environ['JUPYTERHUB_USER'])

################################################################################

# Type Detector

################################################################################

class TypeDetectorHandler(APIHandler):

    @web.authenticated
    async def post(self, *args, **kwargs):
        payload = self.get_json_body()
        types = payload['cell']['types']

        # For each variable in types, write new code with typeof() function
        typesource = ""
        for t in types:
            typesource = typesource + f"\ntypeof({t})"

        self.write(json.dumps({'source': typesource, 'vars': list(types)}))
        self.flush()