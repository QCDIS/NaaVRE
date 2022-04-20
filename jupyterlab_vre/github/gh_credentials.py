class GHCredentials:
    token: str

    def __init__(self, token=None, url=None) -> None:
        self.token = token
        self.url = url
