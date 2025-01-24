import os
from unittest import TestCase
from ..services.secrets_manager.secrets_provider import SecretsProvider

class TestSecretsProvider(TestCase):
    environment_secret_prefix = "Virtual_lab_user_secret_"

    def test_set_secret_new_secret(self):
        secret1_name: str = "secret1"
        secret1_value: str = "secret1_value"
        mock_input = lambda prompt: secret1_value

        SecretsProvider(self.environment_secret_prefix, input_func=mock_input).set_secret(secret1_name)

        self.assertEqual(secret1_value, os.environ[self.environment_secret_prefix + secret1_name])

        self.cleanup_environment_variable(secret1_name)

    def test_set_secret_no_input(self):
        secret1_name: str = "secret1"
        mock_input = lambda prompt: ""

        SecretsProvider(self.environment_secret_prefix, input_func=mock_input).set_secret(secret1_name)

        self.assertIsNone(os.environ.get(self.environment_secret_prefix + secret1_name))

    def test_set_secret_space_input(self):
        secret1_name: str = "secret1"
        mock_input = lambda prompt: " "

        SecretsProvider(self.environment_secret_prefix, input_func=mock_input).set_secret(secret1_name)

        self.assertIsNone(os.environ.get(self.environment_secret_prefix + secret1_name))

    def test_set_secret_overwrite(self):
        secret1_name: str = "secret1"
        secret1_original_value: str = "secret1_original_value"
        secret1_new_value: str = "secret1_new_value"
        os.environ[self.environment_secret_prefix + secret1_name] = secret1_original_value
        mock_input = lambda prompt: secret1_new_value

        SecretsProvider(self.environment_secret_prefix, input_func=mock_input).set_secret(secret1_name)

        self.assertEqual(secret1_new_value, os.environ.get(self.environment_secret_prefix + secret1_name))

        self.cleanup_environment_variable(secret1_name)

    def test_get_secret_nonexistent(self):
        secret1_name: str = "secret1"
        secret1_value: str = "secret1_value"
        mock_input = lambda prompt: secret1_value

        secret_value = SecretsProvider(self.environment_secret_prefix, input_func=mock_input).get_secret(secret1_name)

        self.assertEqual(secret1_value, os.environ[self.environment_secret_prefix + secret1_name], secret_value)

        self.cleanup_environment_variable(secret1_name)

    def test_get_secret_existent(self):
        secret1_name: str = "secret1"
        secret1_value: str = "secret1_value"
        os.environ[self.environment_secret_prefix + secret1_name] = secret1_value

        self.assertEqual(secret1_value, SecretsProvider(self.environment_secret_prefix).get_secret(secret1_name))

        self.cleanup_environment_variable(secret1_name)

    def test_print_secrets(self):
        secret1_name: str = "secret1"
        secret1_value: str = "secret1_value"
        secret2_name: str = "secret2"
        secret2_value: str = "secret2_value"
        os.environ[self.environment_secret_prefix + secret1_name] = secret1_value
        os.environ[self.environment_secret_prefix + secret2_name] = secret2_value

        SecretsProvider(self.environment_secret_prefix).print_secrets()

        self.cleanup_environment_variable(secret1_name)
        self.cleanup_environment_variable(secret2_name)

    def test_print_secrets_no_secrets_stored(self):
        SecretsProvider(self.environment_secret_prefix).print_secrets()

    def test_remove_secret(self):
        secret1_name: str = "secret1"
        secret1_value: str = "secret1_value"
        mock_input = lambda prompt: secret1_value
        os.environ[self.environment_secret_prefix + secret1_name] = secret1_value

        SecretsProvider(self.environment_secret_prefix).remove_secret(secret1_name)

        self.assertIsNone(os.environ.get(self.environment_secret_prefix + secret1_name))

    def cleanup_environment_variable(self, secret_name: str) -> None:
        SecretsProvider(self.environment_secret_prefix).remove_secret(secret_name)