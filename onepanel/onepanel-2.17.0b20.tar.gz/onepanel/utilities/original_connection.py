import os

import functools
import requests
from configparser import ConfigParser


class Connection:
    """ REST API requests defaults and credentials
    """
    def __init__(self):
        self.URL = os.getenv('BASE_API_URL', 'https://c.onepanel.io/api')
        self.SSL_VERIFY = True
        self.headers = {'Content-Type': 'application/json'}
        self.account_uid = None
        self.user_uid = None
        self.token = None
        self.gitlab_impersonation_token = None

        # wrap requests methods to reduce number of arguments in api queries
        self.get = functools.partial(requests.get, headers=self.headers, verify=self.SSL_VERIFY)
        self.post = functools.partial(requests.post, headers=self.headers, verify=self.SSL_VERIFY)
        self.put = functools.partial(requests.put, headers=self.headers, verify=self.SSL_VERIFY)
        self.delete = functools.partial(requests.delete, headers=self.headers, verify=self.SSL_VERIFY)
        self.head = functools.partial(requests.head, headers=self.headers, verify=self.SSL_VERIFY)

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def save_credentials(self, data):
        credentials = ConfigParser()
        credentials['default'] = {'uid': data['uid'],
                                  'token': data['sessions'][0]['token'],
                                  'account_uid': data['account']['uid']}
        if 'gitlab_impersonation_token' in data:
            credentials['default']['gitlab_impersonation_token'] = data['gitlab_impersonation_token']

        onepanel_home = os.path.expanduser(os.path.join('~', '.onepanel'))
        if not os.path.exists(onepanel_home):
            os.makedirs(onepanel_home)

        filename = os.path.join(onepanel_home, 'credentials')
        with open(filename, 'w') as f:
            credentials.write(f)

    def load_credentials(self):
        credentials = ConfigParser()
        filename = os.path.expanduser(os.path.join('~', '.onepanel', 'credentials'))
        credentials.read(filename)

        self.user_uid = credentials.get('default','uid',fallback=None)
        self.account_uid = credentials.get('default', 'account_uid', fallback=None)
        self.token = credentials.get('default', 'token', fallback=None)
        self.gitlab_impersonation_token = credentials.get('default','gitlab_impersonation_token', fallback=None)

        if self.token:
            self.headers['Authorization'] = 'Bearer {}'.format(self.token)

    def set_credentials(self, token, account_uid):
        self.token = token
        self.account_uid = account_uid

        if self.token:
            self.headers['Authorization'] = 'Bearer {}'.format(self.token)

    def clear_credentials(self):
        filename = os.path.expanduser(os.path.join('~', '.onepanel', 'credentials'))

        if not os.path.exists(filename):
            return

        os.remove(filename)
