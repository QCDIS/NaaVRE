import os
import pprint

class SecretsProvider:
    def __init__(self, environment_secret_prefix: str):
        self.environment_secret_prefix = environment_secret_prefix

    def get_secret(self, secret_name: str) -> str:
        try:
            secret_value = os.environ[self.environment_secret_prefix + secret_name]
        except KeyError:
            secret_value = input("The secret does not exist in environment variables. Enter your Secret: ")
            os.environ[self.environment_secret_prefix + secret_name] = secret_value
        return secret_value

    def print_secrets(self):
        secrets_from_environment_variables = {key: value for key, value in os.environ.items() if key.startswith(self.environment_secret_prefix)}
        if secrets_from_environment_variables:
            print(f"\nSecrets in environment variables using the prefix {self.environment_secret_prefix}")
            pprint.pprint(secrets_from_environment_variables, width=1)
        else:
            print(f"\nSecrets using prefix {self.environment_secret_prefix} do not exist in environment variables.")