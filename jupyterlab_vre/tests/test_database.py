import json
import os
import unittest
import uuid
import nbformat as nb

from build.lib.jupyterlab_vre.tests.test_extractor import extract_cell, create_cell
from jupyterlab_vre.database.cell import Cell
from jupyterlab_vre.services.extractor.extractor import Extractor
from jupyterlab_vre.database.database import Catalog


class TestCatalog(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.catalog = Catalog()
        if os.path.exists('resources'):
            self.base_path = 'resources'
        elif os.path.exists('jupyterlab_vre/tests/resources/'):
            self.base_path = 'jupyterlab_vre/tests/resources/'

    def test_add_search_entry(self):
        self.catalog.add_search_entry({'test': 'test'})
        assert self.catalog.get_search_entries() == [{'test': 'test'}]

    def test_delete_all_search_entries(self):
        self.catalog.add_search_entry({'test': 'test'})
        self.catalog.delete_all_search_entries()
        assert self.catalog.get_search_entries() == []

    def test_add_cell(self):
        self.catalog.delete_all_search_entries()
        cell = create_cell(os.path.join(self.base_path, 'notebooks/laserfarm_cells.json'))
        self.catalog.add_cell(cell)
        all_cells = self.catalog.get_all_cells()
        for c in all_cells:
            if c['title'] == cell.title:
                print('cell.__dict__' + str(cell.__dict__))
                print('c.__dict__' + str(c))
                return
        assert False

    def test_delete_cell_from_task_name(self):
        cell = create_cell(os.path.join(self.base_path, 'notebooks/laserfarm_cells.json'))
        self.catalog.add_cell(cell)
        self.catalog.delete_cell_from_task_name(cell.task_name)
        all_cells = self.catalog.get_all_cells()
        for c in all_cells:
            if c['title'] == cell.title:
                assert False

    def test_delete_cell_from_title(self):
        cell = create_cell(os.path.join(self.base_path, 'notebooks/laserfarm_cells.json'))
        self.catalog.add_cell(cell)
        self.catalog.delete_cell_from_title(cell.title)
        all_cells = self.catalog.get_all_cells()
        for c in all_cells:
            if c['title'] == cell.title:
                assert False


    def test_get_all_cells(self):
        cell = create_cell(os.path.join(self.base_path, 'notebooks/laserfarm_cells.json'))
        self.catalog.add_cell(cell)
        cell = create_cell(os.path.join(self.base_path, 'notebooks/MULTIPLY_framework_cells.json'))
        self.catalog.add_cell(cell)
        cell = create_cell(os.path.join(self.base_path, 'notebooks/vol2bird_cells.json'))
        self.catalog.add_cell(cell)
        all_cells = self.catalog.get_all_cells()
        assert len(all_cells) == 3

    def test_get_registry_credentials(self):
        assert self.catalog.get_registry_credentials() == []
    #
    # def test_get_repository_credentials(self):
    #     assert False
    #
    # def test_get_registry_credentials_from_name(self):
    #     assert False
    #
    # def test_add_registry_credentials(self):
    #     assert False
    #
    # def test_add_repository_credentials(self):
    #     assert False
    #
    # def test_get_gh_credentials(self):
    #     assert False
    #
    # def test_delete_all_gh_credentials(self):
    #     assert False
    #
    # def test_delete_all_repository_credentials(self):
    #     assert False
    #
    # def test_delete_all_registry_credentials(self):
    #     assert False
    #
    # def test_add_gh_credentials(self):
    #     assert False
    #
    # def test_delete_gh_credentials(self):
    #     assert False
    #
    # def test_get_credentials_from_username(self):
    #     assert False
    #
    # def test_get_sdia_credentials(self):
    #     assert False
    #
    # def test_get_cell_from_og_node_id(self):
    #     assert False
    #
    # def test_get_repositories(self):
    #     assert False
    #
    # def test_get_repository_from_name(self):
    #     assert False
