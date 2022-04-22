import os
import json
from pathlib import Path
from tinydb import TinyDB, where
from jupyterlab_vre.faircell import Cell
from jupyterlab_vre.sdia.sdia_credentials import SDIACredentials
from jupyterlab_vre.repository.repository_credentials import RepositoryCredentials

class Catalog:

    naa_vre_path = os.path.join(str(Path.home()), 'NaaVRE')
    if not os.path.exists(naa_vre_path):
        os.mkdir(naa_vre_path)

    db               = TinyDB(os.path.join(naa_vre_path, 'db.json'))
    cells            = db.table('cells')
    provision        = db.table('provision')
    sdia_credentials = db.table('sdia_credentials')
    gh_credentials        = db.table('gh_credentials')
    registry_credentials = db.table('registry_credentials')
    editor_buffer: Cell

    @classmethod
    def add_cell(cls, cell: Cell):
        cls.cells.insert(cell.__dict__)

    @classmethod
    def delete_cell_from_title(cls, title: str):
        cls.cells.remove(where('title') == title);

    @classmethod
    def get_all_cells(cls):
        return cls.cells.all()

    @classmethod
    def add_sdia_credentials(cls, cred: SDIACredentials):
        cls.sdia_credentials.insert(cred.__dict__)

    @classmethod
    def add_gh_credentials(cls, cred: RepositoryCredentials):
        cls.gh_credentials.insert(cred.__dict__)

    @classmethod
    def get_gh_credentials(cls) -> RepositoryCredentials:
        credentials = cls.gh_credentials.all()
        if len(credentials) > 0:
            return credentials[0]

    @classmethod
    def add_registry_credentials(cls, cred: RepositoryCredentials):
        cls.registry_credentials.insert(cred.__dict__)

    @classmethod
    def get_registry_credentials(cls) -> RepositoryCredentials:
        credentials = cls.registry_credentials.all()
        if len(credentials) > 0:
            return credentials[0]

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
