import json
import logging
import os
from pathlib import Path

import requests
from notebook.base.handlers import APIHandler
from tornado import web

from jupyterlab_vre.database.database import Catalog

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
module_mapping = {
    'torch.nn': 'torch',
    'torchvision.models': 'torchvision',
    'cv2': 'opencv-python-headless',
    'webdav3': 'webdavclient3'
}


def load_module_names_mapping():
    module_name_mapping_path = os.path.join(str(Path.home()), 'NaaVRE', 'module_name_mapping.json')
    if not os.path.exists(module_name_mapping_path):
        with open(module_name_mapping_path, "w") as module_name_mapping_file:
            json.dump(module_mapping, module_name_mapping_file, indent=4)
    module_name_mapping_file = open(module_name_mapping_path)
    module_name_mapping = json.load(module_name_mapping_file)
    module_name_mapping_file.close()
    return module_name_mapping


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
