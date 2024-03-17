import os
from unittest import TestCase
from jupyterlab_vre.database.catalog import Catalog
from jupyterlab_vre.tests.test_handlers import create_cell_and_add_to_cat


# from jupyterlab_vre.storage.catalog import Catalog


class TestCatalog(TestCase):

    @classmethod
    def setUpClass(self):
        self.catalog = Catalog()
        if os.path.exists('resources'):
            self.base_path = 'resources'
        elif os.path.exists('jupyterlab_vre/tests/resources/'):
            self.base_path = 'jupyterlab_vre/tests/resources/'

    def test_db_path(self):
        self.assertTrue(os.path.exists(Catalog.db_path))

    def test_get_gh_credentials(self):
        gh_credentials = Catalog.get_gh_credentials()
        self.assertIsNotNone(gh_credentials)
        if len(gh_credentials) == 0:
            self.fail()

    def test_get_registry_credentials(self):
        registry_credentials = Catalog.get_registry_credentials()
        if len(registry_credentials) == 0:
            self.fail()
        registry_url = registry_credentials[0]['url']
        self.assertIsNotNone(registry_url)
        cat_repositories = Catalog.get_repositories()
        self.assertIsNotNone(cat_repositories)
        self.assertTrue(len(cat_repositories) > 0)
        repo_token = cat_repositories[0]['token']
        self.assertIsNotNone(repo_token)
        url_repos = cat_repositories[0]['url']
        self.assertIsNotNone(url_repos)
        owner = url_repos.split('https://github.com/')[1].split('/')[0]
        self.assertIsNotNone(owner)
        repository_name = url_repos.split('https://github.com/')[1].split('/')[1]
        self.assertIsNotNone(repository_name)

    def test_update_cell(self):
        cells_json_path = os.path.join(self.base_path, 'cells')
        cells_files = os.listdir(cells_json_path)
        for cell_file in cells_files:
            cell_path = os.path.join(cells_json_path, cell_file)
            test_cell, cell = create_cell_and_add_to_cat(cell_path=cell_path)
            Catalog.delete_cell_from_title(test_cell.title)
            self.assertIsNotNone(test_cell)
            self.assertIsNotNone(cell)
            Catalog.add_cell(test_cell)
            document_cell = Catalog.get_cell_from_og_node_id(test_cell.node_id)
            returned_cell = Catalog.cast_document_to_cell(document_cell)
            self.assertIsNotNone(returned_cell)
            self.assertEqual(returned_cell.title, test_cell.title)
            self.assertEqual(returned_cell.task_name, test_cell.task_name)
            self.assertEqual(returned_cell.node_id, test_cell.node_id)

            # Modify cell source and update
            returned_cell.original_source = 'modified'
            Catalog.update_cell(returned_cell)
            modified_cell_doc = Catalog.get_cell_from_og_node_id(test_cell.node_id)
            modified_cell = Catalog.cast_document_to_cell(modified_cell_doc)
            self.assertEqual(modified_cell.original_source, 'modified')
            self.assertEqual(modified_cell.title, test_cell.title)
            self.assertEqual(modified_cell.task_name, test_cell.task_name)
            self.assertEqual(modified_cell.node_id, test_cell.node_id)
            Catalog.delete_cell_from_title(test_cell.title)
            deleted_cell = Catalog.get_cell_from_og_node_id(test_cell.node_id)
            self.assertIsNone(deleted_cell)
            all_cells = Catalog.get_all_cells()
            for cell in all_cells:
                if cell['node_id'] == test_cell.node_id:
                    self.fail()
            Catalog.delete_all_cells()
            all_cells = Catalog.get_all_cells()
            self.assertEqual(len(all_cells), 0)






