import os
from unittest import TestCase


# from jupyterlab_vre.storage.catalog import Catalog


class TestEnvironmentVariables(TestCase):

    def test_env_vars(self):
        self.assertIsNotNone(os.environ.get('CELL_GITHUB'))
        self.assertIsNotNone(os.environ.get('CELL_GITHUB_TOKEN'))
        self.assertIsNotNone(os.environ.get('REGISTRY_URL'))
        self.assertIsNotNone(os.environ.get('NAAVRE_API_TOKEN'))
        self.assertIsNotNone(os.environ.get('JUPYTERHUB_USER'))
        self.assertIsNotNone(os.environ.get('API_ENDPOINT'))
        self.assertIsNotNone(os.environ.get('VLAB_SLUG'))
        self.assertIsNotNone(os.environ.get('MODULE_MAPPING_URL'))
        self.assertIsNotNone(os.environ.get('SEARCH_API_ENDPOINT'))
        self.assertIsNotNone(os.environ.get('SEARCH_API_TOKEN'))
        self.assertIsNotNone(os.environ.get('ARGO_URL'))


