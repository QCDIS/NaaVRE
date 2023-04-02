import os
from unittest import TestCase
from github import Github
from jupyterlab_vre.database.database import Catalog

# from jupyterlab_vre.storage.catalog import Catalog


class TestCatalog(TestCase):

    @classmethod
    def setUpClass(self):
        self.catalog = Catalog()
        if os.path.exists('resources'):
            self.base_path = 'resources'
        elif os.path.exists('jupyterlab_vre/tests/resources/'):
            self.base_path = 'jupyterlab_vre/tests/resources/'

    def test_get_registry_credentials(self):
        registry_credentials = Catalog.get_registry_credentials()
        if len(registry_credentials) == 0:
            self.fail()

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


