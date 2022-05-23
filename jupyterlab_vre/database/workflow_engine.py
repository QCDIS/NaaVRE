

from lib2to3.pgen2 import token
from nturl2path import url2pathname
from unicodedata import name


class WorkflowEngine:

    name        : str
    url         : str
    token       : str
    provider    : str

    def __init__(self, name, url, token, provider) -> None:
        
        self.name       = name
        self.url        = url
        self.token      = token
        self.provider   = provider
