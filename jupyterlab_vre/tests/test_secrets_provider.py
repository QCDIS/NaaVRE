from unittest import TestCase
from yaml import YAMLError
from ..services.secrets_manager.secrets_provider import SecretsProvider

class TestSecretsProvider(TestCase):
    def test_file_not_found(self):
        incorrect_file_path: str = "../file_does_not_exist.yaml"
        with self.assertRaises(FileNotFoundError):
            SecretsProvider(incorrect_file_path)

    def test_not_parsed_to_dict(self):
        not_parsed_to_dict_file_path: str = "jupyterlab_vre/tests/resources/secrets/secrets_not_in_yaml_format.yaml"
        with self.assertRaises(SyntaxError):
            SecretsProvider(not_parsed_to_dict_file_path)

    def test_YAML_error(self):
        polluted_file_path: str = "jupyterlab_vre/tests/resources/secrets/polluted_secrets_file.yaml"
        with self.assertRaises(YAMLError):
            SecretsProvider(polluted_file_path)

    def test_retrieve_secret(self):
        secret_file_path: str = "jupyterlab_vre/tests/resources/secrets/secrets.yaml"
        KNMI_key_name: str = "KNMI_OPEN_DATA_API_KEY"
        KNMI_OPEN_DATA_API_KEY: str = "eyJvcmciOiI1ZTU1NGUxOTI3NGE5NjAwMDEyYTNlYjEiLCJpZCI6ImRlMGNiMGM5ZjM2NTQyYjU4YWU1MmUwODMxNGExMDcwIiwiaCI6Im11cm11cjEyOCJ9"
        self.assertEqual(KNMI_OPEN_DATA_API_KEY, SecretsProvider(secret_file_path).get_secret(KNMI_key_name))
