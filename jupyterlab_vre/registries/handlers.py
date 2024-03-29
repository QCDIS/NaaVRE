import json

from notebook.base.handlers import APIHandler
from tornado import web

from jupyterlab_vre.database.catalog import Catalog


class RegistriesHandler(APIHandler, Catalog):

    @web.authenticated
    async def get(self):
        registries = Catalog.get_registry_credentials()
        self.write(json.dumps(registries))
        self.flush()
