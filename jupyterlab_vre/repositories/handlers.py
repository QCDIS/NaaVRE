
import copy
import json
import uuid

from jupyterlab_vre.database.database import Catalog
from notebook.base.handlers import APIHandler
from tornado import web


class RepositoriesHandler(APIHandler, Catalog):

    @web.authenticated
    async def get(self):
        repositories = Catalog.get_repositories()
        self.write(json.dumps(repositories))
        self.flush()
