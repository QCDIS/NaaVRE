import requests
from requests.models import HTTPBasicAuth

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
            print("In ex")
            return ex