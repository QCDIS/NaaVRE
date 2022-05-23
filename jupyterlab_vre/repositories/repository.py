

from lib2to3.pgen2 import token
from unicodedata import name
from urllib.request import urlopen


class Repository:

    name    : str
    url     : str
    token   : str

    def __init__(self, name, url, token) -> None:
        
        self.name   = name
        self.url    = url
        self.token  = token