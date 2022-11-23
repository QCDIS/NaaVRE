import argparse
import json
import logging
import os
from pathlib import Path

from jupyterlab_vre.database.database import Catalog
from jupyterlab_vre.repositories.repository import Repository

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

arg_parser = argparse.ArgumentParser()

arg_parser.add_argument('--force', action='store', type=bool, required='True', dest='force')
arg_parser.add_argument('--github_url', action='store', type=str, required='True', dest='github_url')
arg_parser.add_argument('--github_token', action='store', type=str, required='True', dest='github_token')

arg_parser.add_argument('--registry_url', action='store', type=str, required='True', dest='registry_url')
# arg_parser.add_argument('--registry_token', action='store', type=str, required='True', dest='registry_token')

args = arg_parser.parse_args()

force = args.force
github_url = args.github_url
github_token = args.github_token

registry_url = args.registry_url


# registry_token = args.registry_token


def add_gh_credentials(force_replace=None, repository_credentials=None):
    if force_replace:
        Catalog.delete_all_gh_credentials()
        Catalog.add_gh_credentials(repository_credentials)
    else:
        gh_credentials = Catalog.get_gh_credentials()
        if not gh_credentials:
            Catalog.add_gh_credentials(repository_credentials)


def add_registry_credentials(force_replace, registry_credentials):
    if force_replace:
        Catalog.delete_all_registry_credentials()
        Catalog.add_registry_credentials(registry_credentials)
    else:
        registry_credentials = Catalog.get_gh_credentials()
        if not registry_credentials:
            Catalog.add_registry_credentials(registry_credentials)


def add_repository_credentials(force_replace, repository_credentials):
    if force_replace:
        Catalog.delete_all_repository_credentials()
        Catalog.add_repository_credentials(repository_credentials)
    else:
        gh_credentials = Catalog.get_repository_credentials()
        if not gh_credentials:
            Catalog.add_repository_credentials(repository_credentials)


if __name__ == '__main__':
    input_repository_credentials = Repository(github_url.split('https://github.com/')[1], github_url, github_token)
    add_gh_credentials(force_replace=force, repository_credentials=input_repository_credentials)
    add_repository_credentials(force_replace=force, repository_credentials=input_repository_credentials)

    input_registry_credentials = Repository(registry_url.split('https://hub.docker.com/')[1], registry_url, None)
    add_registry_credentials(force_replace=force, registry_credentials=input_registry_credentials)
