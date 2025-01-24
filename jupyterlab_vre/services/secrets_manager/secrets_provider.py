import os
import pprint

class SecretsProvider:
    def __init__(self, environment_secret_prefix: str, input_func=input):
        self.environment_secret_prefix = environment_secret_prefix
        self.get_input = input_func

    def set_secret(self, secret_name: str):
        '''Saves a secret in environment variables from user input.
        If there is already a secret with the name given. Entering a new value will overwrite the existing secret.
        '''
        current_secret_value: str = os.environ.get(self.environment_secret_prefix + secret_name)
        if (current_secret_value):
            print(f"\nThere is already a secret named {secret_name} stored as {self.environment_secret_prefix + secret_name}. Entering a new value will overwrite the existing secret.")
        new_secret_value = self._request_secret_value()
        self._store_secret(secret_name, new_secret_value)

    def get_secret(self, secret_name: str) -> str:
        '''Retrieves secret from environment variables
        looks for an environment variable environment_secret_prefix + secret_name
        if this secret does not exist, it prompts the user to enter a secret and stores that to environment variables.
        '''
        secret_value = os.environ.get(self.environment_secret_prefix + secret_name)
        if not secret_value:
            print(f"\nA secret with name {self.environment_secret_prefix + secret_name} is not yet stored in environment variables.")
            secret_value = self._request_secret_value()
            self._store_secret(secret_name, secret_value)
        return secret_value

    def remove_secret(self, secret_name: str) -> None:
        '''Remove the secret from environment variables'''
        os.environ.pop(self.environment_secret_prefix + secret_name)

    def print_secrets(self) -> None:
        '''Prints secrets in environment variables which have the environment_secret_prefix'''
        secrets_from_environment_variables = {key: value for key, value in os.environ.items() if key.startswith(self.environment_secret_prefix)}
        if secrets_from_environment_variables:
            print(f"\nThere are {len(secrets_from_environment_variables)} secret(s) in environment variables using the prefix {self.environment_secret_prefix}")
            pprint.pprint(secrets_from_environment_variables, width=1)
        else:
            print(f"\nSecrets using prefix {self.environment_secret_prefix} do not exist in environment variables.")

    def _request_secret_value(self) -> str:
        return self.get_input("Enter your Secret: ")

    def _store_secret(self, secret_name: str, secret_value: str) -> None:
        if secret_value.strip():
            os.environ[self.environment_secret_prefix + secret_name] = secret_value
            print(f"\nSecret has been stored as environment variable: {self.environment_secret_prefix + secret_name}.")
        else:
            print("\nNo value entered for the secret. Not storing.")