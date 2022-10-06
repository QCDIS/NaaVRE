
import copy
import json
import uuid

from jupyterlab_vre.database.database import Catalog
from notebook.base.handlers import APIHandler
from tornado import web


class RegistriesHandler(APIHandler, Catalog):

    @web.authenticated
    async def get(self):
        registries = Catalog.get_registry_credentials()
        print(registries)
        self.write(json.dumps(registries))
        self.flush()
