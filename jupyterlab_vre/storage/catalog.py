import json
from tinydb import TinyDB, where
from jupyterlab_vre.faircell import Cell
from jupyterlab_vre.sdia.credentials import SDIACredentials

class Catalog:

    db          = TinyDB('db.json')
    cells       = db.table('cells')
    provision   = db.table('provision')
    credentials = db.table('credentials')
    editor_buffer: Cell

    @classmethod
    def add_cell(cls, cell: Cell):
        cls.cells.insert(cell.__dict__)

    @classmethod
    def get_all_cells(cls):
        return cls.cells.all()

    @classmethod
    def add_credentials(cls, cred: SDIACredentials):
        cls.credentials.insert(cred.__dict__)

    @classmethod
    def get_cell_from_og_node_id(cls, og_node_id) -> Cell:
        res = cls.cells.search(where('node_id') == og_node_id)
        if (res):
            return res[0]