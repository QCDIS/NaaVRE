import json

from notebook.base.handlers import APIHandler
from tornado import web

from jupyterlab_vre.database.catalog import Catalog


class RepositoriesHandler(APIHandler, Catalog):

    @web.authenticated
    async def get(self):
        repositories = Catalog.get_repositories()
        self.write(json.dumps(repositories))
        self.flush()
