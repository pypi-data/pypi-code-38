import requests
import bs4
import re
from gt.sources.base import GitSource

class Gitlab(GitSource):
    """
    Class for manipulating private projects hosted by gitlab (the service).
    Scraping is used in place of the API which is painfully slow
    (see https://gitlab.com/gitlab-com/support-forum/issues/576 and
    https://gitlab.com/gitlab-com/gl-infra/infrastructure/issues/59). The 
    constructor consumes an API access token which can be generated
    here: https://gitlab.com/profile/personal_access_tokens.
    """
    
    def __init__(self, api_token):
        self.http = requests.Session()
        self.http.headers.update({'PRIVATE-TOKEN': api_token})
        
    @property
    def repos(self):
        page = 1
        res = []

        if not hasattr(self, '_repo_cache'):
            self._repo_cache = {}

            while True:
                resp = self.http.get('https://gitlab.com/api/v4/projects?owned=true&per_page=100&page=' + str(page))
                page = resp.headers['X-Next-Page']
                self._repo_cache.update({ r['name']: r for r in resp.json() })
                if not page: break

        return [  (k, v['visibility'] == 'private') for k,v in self._repo_cache.items() ]

    def delete(self, name):
        if not hasattr(self, '_repo_cache'):
            self.list()

        if name not in self._repo_cache:
            raise Exception('Repo "%s" does not exist' % name)

        _id = self._repo_cache[name]['id']
        r = self.http.delete('https://gitlab.com/api/v4/projects/' + str(_id))
        if r.status_code != 202:
            raise Exception()

    def git_url(self, name):
        if not hasattr(self, '_repo_cache'):
            self.repos

        url = self._repo_cache[name]['ssh_url_to_repo']
        url = url.replace('gitlab.com:', 'gitlab.com:/')

        return 'ssh://' + url
    
    def create(self, name, is_private=True, description=''):
        r = self.http.post('https://gitlab.com/api/v4/projects', {'path': name, 'description': description, 'visibility': 'private' if is_private else 'public' })
        if r.status_code != 201:
            raise Exception('Gitlab creation failed (project already exists?).')
