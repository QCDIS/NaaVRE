import os
from unittest import TestCase
from ..services.secrets_manager.secrets_provider import SecretsProvider

class TestSecretsProvider(TestCase):
    environment_secret_prefix = "Virtual_lab_user_secret_"

    def test_retrieve_secret(self):
        secret1_name: str = "secret1"
        secret1_value: str = "secret1_value"
        os.environ[self.environment_secret_prefix + secret1_name] = secret1_value

        self.assertEqual(secret1_value, SecretsProvider(self.environment_secret_prefix).get_secret(secret1_name))

        self.clean_secret(secret1_name)

    def test_retrieve_nonexistent_secret(self):
        secret1_name: str = "secret1"
        with self.assertRaises(OSError):
            SecretsProvider(self.environment_secret_prefix).get_secret(secret1_name)

    def test_print_secret(self):
        secret1_name: str = "secret1"
        secret1_value: str = "secret1_value"
        secret2_name: str = "secret2"
        secret2_value: str = "secret2_value"
        os.environ[self.environment_secret_prefix + secret1_name] = secret1_value
        os.environ[self.environment_secret_prefix + secret2_name] = secret2_value

        SecretsProvider(self.environment_secret_prefix).print_secrets()

        self.clean_secret(secret1_name)
        self.clean_secret(secret2_name)

    def test_print_no_secrets(self):
        SecretsProvider(self.environment_secret_prefix).print_secrets()

    def clean_secret(self, secret_name: str):
        os.environ.pop(self.environment_secret_prefix + secret_name)