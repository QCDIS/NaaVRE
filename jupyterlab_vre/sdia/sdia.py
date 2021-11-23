import requests
from requests.models import HTTPBasicAuth
from .sdia_credentials import SDIACredentials

class SDIA:

    @staticmethod
    def test_auth(username, password, endpoint):

        try:

            return requests.get(
                endpoint,
                auth=HTTPBasicAuth(username,password),
                verify=False
            )
        
        except Exception as ex:
            return ex

    @staticmethod
    def provision(credentials: SDIACredentials, template_id):

        provision_path = credentials['endpoint'] + 'orchestrator/provisioner/provision/' + template_id
        print(provision_path)

        try:

            return requests.get(
                provision_path,
                auth=HTTPBasicAuth(
                    credentials['username'],
                    credentials['password']
                ),
                verify=False,
                headers={'accept': 'text/plain'}
            )

        except Exception as ex:
            return ex