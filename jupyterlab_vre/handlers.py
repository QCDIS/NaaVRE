import copy
import json
import logging
import os
import uuid
from builtins import Exception
from pathlib import Path

import autopep8
import nbformat as nb
import requests
from github3 import login
from jinja2 import Environment, PackageLoader
from notebook.base.handlers import APIHandler
from tornado import web

from jupyterlab_vre.sdia.sdia import SDIA
from jupyterlab_vre.sdia.sdia_credentials import SDIACredentials
from jupyterlab_vre.database.database import Catalog
from jupyterlab_vre.database.cell import Cell
from jupyterlab_vre.services.parser.parser import WorkflowParser

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
module_mapping = {'fnmatch': 'fnmatch2'}
standard_library = [
    'pathlib',
    'time',
    'os',
    'fileinput',
    'tempfile',
    'glob',
    'sys',
    'stat',
    'filecmp',
    'linecache',
    'shutil',
    'logging',
    'socket',
    'array',
    'ssl',
    'datetime',
    'smtplib',
    'selectors',
    'asyncio',
    'sys',
    'signal',
    'asynchat',
    'mmap',
    'multiprocessing',
    'concurrent',
    'urllib',
    'math',
    'shlex',
    'subprocess',
    'sched',
    'threading',
    'dummy_threading',
    'io',
    'argparse',
    'getopt',
    'random'
]

################################################################################

# Catalog

################################################################################

def load_standard_library_names():
    standard_library_names_path = os.path.join(str(Path.home()), 'NaaVRE', 'standard_library_names.json')
    if not os.path.exists(standard_library_names_path):
        with open(standard_library_names_path, "w") as standard_library_names_file:
            json.dump(standard_library, standard_library_names_file, indent=4)
    standard_library_names_file = open(standard_library_names_path)
    part_of_standard_library = json.load(standard_library_names_file)
    return part_of_standard_library


def load_module_names_mapping():
    module_name_mapping_path = os.path.join(str(Path.home()), 'NaaVRE', 'module_name_mapping.json')
    if not os.path.exists(module_name_mapping_path):
        with open(module_name_mapping_path, "w") as module_name_mapping_file:
            json.dump(module_mapping, module_name_mapping_file, indent=4)
    module_name_mapping_file = open(module_name_mapping_path)
    module_name_mapping = json.load(module_name_mapping_file)
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

