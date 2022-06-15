

from unicodedata import name


class ImageRegistry:

    name        : str
    url         : str
    token       : str
    provider    : str

    def __init__(self, name, url, token, provider) -> None:
        
        self.name       = name
        self.url        = url
        self.token      = token
        self.provider   = provider