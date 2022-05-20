import logging


class TokenCredentials:

    provider    : str    
    token       : str
    url         : str

    def __init__(self, token=None, url=None) -> None:

        self.token  = token
        self.url    = url
