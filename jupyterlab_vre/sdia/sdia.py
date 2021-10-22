import requests

class SDIA:

    @staticmethod
    def test_auth(username, password):
        response = requests.head('https://lifewatch.lab.uvalight.net:30003/orchestrator/provisioner/provision/60d1b449c2ecb8079ee65988')