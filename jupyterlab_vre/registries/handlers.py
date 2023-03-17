import json

from notebook.base.handlers import APIHandler
from tornado import web

from jupyterlab_vre.database.database import Catalog


class RegistriesHandler(APIHandler, Catalog):

    @web.authenticated
    async def get(self):
        registries = Catalog.get_registry_credentials()
        print(registries)
        self.write(json.dumps(registries))
        self.flush()
