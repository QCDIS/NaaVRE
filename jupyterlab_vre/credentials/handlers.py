import json

from jupyterlab_vre.storage.catalog import Catalog
from notebook.base.handlers import APIHandler
from tornado import web


class CredentialsHandler(APIHandler, Catalog):

    @web.authenticated
    async def post(self, *args, **kwargs):
        msg_json = dict(title="Operation not supported.")
        self.write(msg_json)
        self.flush()

    @web.authenticated
    async def get(self):
        credentials = Catalog.get_all_credentials()
        self.write(json.dumps(credentials))
        self.flush()
