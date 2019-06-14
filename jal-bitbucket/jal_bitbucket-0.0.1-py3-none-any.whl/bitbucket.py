import os
import requests

from requests.auth import HTTPBasicAuth

USER = os.environ.get('BITBUCKET_USER')
PASSWORD = os.environ.get('BITBUCKET_API_KEY')
AUTH = HTTPBasicAuth(USER, PASSWORD)
API_VERSION = '2.0'


class BitBucketAPIException(Exception):
    """Base class for API errors"""
    pass


def _api_call(url, **kwargs):
    method = kwargs.get('method')
    if method:
        del kwargs['method']
    else:
        method = requests.get
    request = method(url, **kwargs)
    if not request.ok:
        raise BitBucketAPIException(f"API ERROR\n{request.text}")
    data = request.json()
    return data


class BitBucket:
    base_url = f"https://api.bitbucket.org/{API_VERSION}/"

    def __init__(self, workspace=None):
        self.workspace = workspace

    def __repr__(self):
        return f"BitBucket API\nWorkspace: {self.workspace}\n"

    def get_user_pull_requests(self, username):
        url = f"{self.base_url}pullrequests/{username}"
        data = _api_call(url, method=requests.get, auth=AUTH)
        return data['values']

    def get_workspace_repos(self, workspace):
        url = f"{self.base_url}repositories/{workspace}"
        data = _api_call(url, method=requests.get, auth=AUTH)
        return data['values']

    def get_repo(self, repo, workspace):
        url = f"{self.base_url}repositories/{workspace}/{repo}"
        data = _api_call(url, method=requests.get, auth=AUTH)
        return data


def main():
    bitbucket = BitBucket()
    print(bitbucket)


if __name__ == '__main__':
    main()
