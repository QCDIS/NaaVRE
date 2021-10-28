import requests
from requests.models import HTTPBasicAuth

class SDIA:

    @staticmethod
    def test_auth(username, password, endpoint):
        return requests.get(
            endpoint,
            auth=HTTPBasicAuth(username,password),
            verify=False
        )