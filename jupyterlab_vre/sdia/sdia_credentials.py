class SDIACredentials:
    username: str
    password: str
    endpoint: str

    def __init__(self, username, password, endpoint) -> None:
        self.username = username
        self.password = password
        self.endpoint = endpoint
