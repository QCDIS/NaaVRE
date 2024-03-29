import json
import logging
import os
from pathlib import Path

import requests
from notebook.base.handlers import APIHandler
from tornado import web

from jupyterlab_vre.database.catalog import Catalog

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def load_module_names_mapping():
    module_mapping_url = os.getenv('MODULE_MAPPING_URL')
    loaded_module_mapping = {}
    if module_mapping_url:
        resp = requests.get(module_mapping_url)
        loaded_module_mapping = json.loads(resp.text)
    module_name_mapping_path = os.path.join(
        str(Path.home()), 'NaaVRE', 'module_name_mapping.json')
    if not os.path.exists(module_name_mapping_path):
        with open(module_name_mapping_path, 'w') as module_name_mapping_file:
            json.dump(loaded_module_mapping, module_name_mapping_file, indent=4)
        module_name_mapping_file.close()

    module_name_mapping_file = open(module_name_mapping_path)
    loaded_module_name_mapping = json.load(module_name_mapping_file)
    loaded_module_name_mapping.update(loaded_module_mapping)
    module_name_mapping_file.close()
    return loaded_module_name_mapping


@web.authenticated
async def delete(self, *args, **kwargs):
    payload = self.get_json_body()
    Catalog.delete_cell_from_title(payload['title'])


class CatalogGetAllHandler(APIHandler, Catalog):

    @web.authenticated
    async def get(self):
        self.write(json.dumps(Catalog.get_all_cells()))
        self.flush()

    @web.authenticated
    async def post(self, *args, **kwargs):
        msg_json = dict(title="Operation not supported.")
        self.write(msg_json)
        self.flush()
