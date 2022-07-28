class Repository:

    name    : str
    url     : str
    token   : str

    def __init__(self, name, url, token) -> None:
        
        self.name   = name
        self.url    = url
        self.token  = token