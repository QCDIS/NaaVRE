import logging
import os
from pathlib import Path
from tinydb import TinyDB, where

from jupyterlab_vre.database.cell import Cell
from jupyterlab_vre.repositories.repository import Repository

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Catalog:
    naa_vre_path = os.path.join(str(Path.home()), 'NaaVRE')
    if not os.path.exists(naa_vre_path):
        os.mkdir(naa_vre_path)

    db = TinyDB(os.path.join(naa_vre_path, 'db.json'))

    cells = db.table('cells')
    workflows = db.table('workflows')
    provision = db.table('provision')
    sdia_credentials = db.table('sdia_credentials')
    gh_credentials = db.table('gh_credentials')
    registry_credentials = db.table('registry_credentials')

    editor_buffer: Cell

    @classmethod
    def add_cell(cls, cell: Cell):
        cls.cells.insert(cell.__dict__)

    @classmethod
    def delete_cell_from_task_name(cls, task_name: str):
        cell = cls.cells.search(where('task_name') == task_name)
        cls.cells.remove(where('task_name') == task_name)

    @classmethod
    def delete_cell_from_title(cls, title: str):
        cell = cls.cells.search(where('title') == title)
        cls.cells.remove(where('title') == title)

    @classmethod
    def get_all_cells(cls):
        return cls.cells.all()

    @classmethod
    def add_registry_credentials(cls, cred: Repository):
        cls.registry_credentials.insert(cred.__dict__)

    @classmethod
    def delete_registry_credentials(cls, url: str):
        cls.registry_credentials.remove(where('url') == url)

    @classmethod
    def delete_all_registry_credentials(cls):
        # Looks bad but for now I could not find a way to remove all
        credentials = cls.registry_credentials.all()
        ids = []
        for credential in credentials:
            ids.append(credential.doc_id)
        cls.registry_credentials.remove(doc_ids=ids)

    @classmethod
    def get_registry_credentials(cls) -> Repository:
        credentials = cls.registry_credentials.all()
        if len(credentials) > 0:
            return credentials[0]

    @classmethod
    def add_gh_credentials(cls, cred: Repository):
        cls.gh_credentials.insert(cred.__dict__)

    @classmethod
    def get_gh_credentials(cls) -> Repository:
        credentials = cls.gh_credentials.all()
        if len(credentials) > 0:
            return credentials[0]

    @classmethod
    def delete_all_gh_credentials(cls):
        # Looks bad but for now I could not find a way to remove all
        credentials = cls.gh_credentials.all()
        ids = []
        for credential in credentials:
            ids.append(credential.doc_id)
        cls.gh_credentials.remove(doc_ids=ids)

    @classmethod
    def delete_gh_credentials(cls, url: str):
        cls.gh_credentials.remove(where('url') == url)


    @classmethod
    def get_sdia_credentials(cls):
        return cls.sdia_credentials.all()

    @classmethod
    def get_cell_from_og_node_id(cls, og_node_id) -> Cell:
        res = cls.cells.search(where('node_id') == og_node_id)
        if res:
            return res[0]
