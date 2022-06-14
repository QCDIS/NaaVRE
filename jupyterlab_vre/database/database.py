import logging
import os
import json
from pathlib import Path
from jupyterlab_vre.repositories.repository import Repository
from tinydb import TinyDB, where
from jupyterlab_vre.database.cell import Cell
from jupyterlab_vre.sdia.sdia_credentials import SDIACredentials

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Catalog:

    naa_vre_path = os.path.join(str(Path.home()), 'NaaVRE')

    if not os.path.exists(naa_vre_path):
        os.mkdir(naa_vre_path)

    db = TinyDB(os.path.join(naa_vre_path, 'NaaVRE_db.json'))

    cells               = db.table('cells')
    workflows           = db.table('workflows')
    repositories        = db.table('repositories')
    image_registries    = db.table('image_registries')
    workflow_engines    = db.table('workflow_engines')

    editor_buffer: Cell

    @classmethod
    def add_cell(cls, cell: Cell):
        cls.cells.insert(cell.__dict__)

    @classmethod
    def delete_cell_from_title(cls, title: str):
        cls.cells.remove(where('title') == title)

    @classmethod
    def get_all_cells(cls):
        return cls.cells.all()

    @classmethod
    def get_cell_from_og_node_id(cls, og_node_id) -> Cell:
        res = cls.cells.search(where('node_id') == og_node_id)
        if res:
            return res[0]

    @classmethod
    def get_repositories(cls) -> list:
        res = cls.repositories.all()
        return res

