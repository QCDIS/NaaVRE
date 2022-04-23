import logging

logger = logging.getLogger(__name__)


class RepositoryCredentials:
    token: str
    url: str

    def __init__(self, token=None, url=None) -> None:
        self.token = token
        self.url = url
