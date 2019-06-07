"""Functions calling GitHub API."""

import requests

API_BASE_URL = "https://api.github.com/repos"
RAW_BASE_URL = "https://raw.githubusercontent.com"


def build_schema_url(project_path, ref, schema_filename):
    return "{}/{}/{}/{}".format(RAW_BASE_URL, project_path, ref, schema_filename)


def iter_refs(project_path):
    """Yield tuples of tags and branches defined in the given repository.

    e.g. [('tag', 'v0.0.1'), ('branch', 'master'), ('tag', 'v2.0.0')]
    """
    tags_url = '{}/{}/tags'.format(API_BASE_URL, project_path)
    response = requests.get(tags_url)
    response.raise_for_status()
    for tag in response.json():
        yield ('tag', tag['name'])
    branches_url = '{}/{}/branches'.format(API_BASE_URL, project_path)
    response = requests.get(branches_url)
    response.raise_for_status()
    for branch in response.json():
        yield ('branch', branch['name'])
