import logging
import os
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

    cells = db.table('cells')
    workflows = db.table('workflows')
    repositories = db.table('repositories')
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
    def get_registry_credentials(cls):
        credentials = cls.registry_credentials.all()
        return credentials

    @classmethod
    def get_repository_credentials(cls):
        credentials = cls.repository.all()
        return credentials

    @classmethod
    def get_registry_credentials_from_name(cls, name: str):
        res = cls.registry_credentials.search(where('name') == name)
        if res:
            return res[0]

    @classmethod
    def add_registry_credentials(cls, cred: Repository):
        cls.registry_credentials.insert(cred.__dict__)


    @classmethod
    def add_repository_credentials(cls, cred: Repository):
        cls.repositories.insert(cred.__dict__)

    @classmethod
    def get_gh_credentials(cls):
        credentials = cls.gh_credentials.all()
        if len(credentials) > 0:
            return credentials[0]

    @classmethod
    def delete_all_gh_credentials(cls):
        cls.gh_credentials.truncate()

    @classmethod
    def delete_all_repository_credentials(cls):
        cls.repositories.truncate()
        credentials = cls.repositories.all()
        ids = []
        for credential in credentials:
            ids.append(credential.doc_id)
        cls.repositories.remove(doc_ids=ids)
        cls.repositories.truncate()

    @classmethod
    def delete_all_registry_credentials(cls):
        # Looks bad but for now I could not find a way to remove all
        credentials = cls.registry_credentials.all()
        ids = []
        for credential in credentials:
            ids.append(credential.doc_id)
        cls.registry_credentials.remove(doc_ids=ids)
        cls.registry_credentials.truncate()

    @classmethod
    def add_gh_credentials(cls, cred: Repository):
        cls.repositories.insert(cred.__dict__)
        cls.gh_credentials.insert(cred.__dict__)

    @classmethod
    def delete_gh_credentials(cls, url: str):
        cls.gh_credentials.remove(where('url') == url)

    @classmethod
    def get_credentials_from_username(cls, cred_username) -> SDIACredentials:
        res = cls.sdia_credentials.search(where('username') == cred_username)
        if res:
            return res[0]

    @classmethod
    def get_sdia_credentials(cls):
        return cls.sdia_credentials.all()

    @classmethod
    def get_cell_from_og_node_id(cls, og_node_id) -> Cell:
        res = cls.cells.search(where('node_id') == og_node_id)
        if res:
            return res[0]

    @classmethod
    def get_repositories(cls) -> list:
        res = cls.repositories.all()
        return res

    @classmethod
    def get_repository_from_name(cls, name: str) -> Repository:
        res = cls.repositories.search(where('name') == name)
        if res:
            return res[0]
