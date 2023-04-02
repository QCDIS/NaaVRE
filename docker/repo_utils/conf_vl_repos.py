import argparse
import logging
import os
from pathlib import Path

from tinydb import TinyDB, where

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

arg_parser = argparse.ArgumentParser()

naa_vre_path = os.path.join(str(Path.home()), 'NaaVRE')

if not os.path.exists(naa_vre_path):
    os.mkdir(naa_vre_path)

db_path = os.path.join(naa_vre_path, 'NaaVRE_db.json')
db = TinyDB(db_path)

cells = db.table('cells')
workflows = db.table('workflows')
repositories = db.table('repositories')
gh_credentials = db.table('gh_credentials')
registry_credentials = db.table('registry_credentials')
search_entry = db.table('search_entries')

arg_parser.add_argument('--force', action='store', type=bool, required='True', dest='force')
args = arg_parser.parse_args()

force = args.force


def add_gh_credentials(force_replace=None, repository_credentials=None):
    if force_replace:
        gh_credentials.remove(where('url') == repository_credentials['url'])
    gh_credentials.insert(repository_credentials)


def add_registry_credentials(force_replace, input_registry_credentials):
    if force_replace:
        registry_credentials.remove(where('url') == input_registry_credentials['url'])
    registry_credentials.insert(input_registry_credentials)


def add_repository_credentials(force_replace, repository_credentials):
    if force_replace:
        repositories.remove(where('url') == repository_credentials['url'])
    repositories.insert(repository_credentials)


if __name__ == '__main__':
    github_url = os.getenv('CELL_GITHUB')
    github_token = os.getenv('CELL_GITHUB_TOKEN')
    registry_url = os.getenv('REGISTRY_URL')

    print(github_url)
    input_repository_credentials = {'name': github_url.split('https://github.com/')[1], 'url': github_url,
                                    'token': github_token}
    add_gh_credentials(force_replace=force, repository_credentials=input_repository_credentials)
    add_repository_credentials(force_replace=force, repository_credentials=input_repository_credentials)

    input_registry_credentials = {'name': registry_url.split('https://hub.docker.com/')[1], 'url': registry_url,
                                  'token': None}
    add_registry_credentials(force_replace=force, input_registry_credentials=input_registry_credentials)
