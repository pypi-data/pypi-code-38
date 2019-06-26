import os
import functools
import six
if six.PY2:
    import ConfigParser as configparser
else:
    import configparser
import requests

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

    def save_credentials(self, data):
        credentials = configparser.ConfigParser()
        credentials.add_section('onepanel')
        credentials.set('onepanel','uid',data['uid'])
        credentials.set('onepanel','token',data['sessions'][0]['token'])
        credentials.set('onepanel','account_uid',data['account']['uid'])
        if 'gitlab_impersonation_token' in data:
            credentials.set('onepanel','gitlab_impersonation_token', data['gitlab_impersonation_token'])

        onepanel_home = os.path.expanduser(os.path.join('~', '.onepanel'))
        if not os.path.exists(onepanel_home):
            os.makedirs(onepanel_home)

        filename = os.path.join(onepanel_home, 'credentials')
        with open(filename, 'w') as f:
            credentials.write(f)

    def load_credentials(self):
        credentials = configparser.ConfigParser()
        filename = os.path.expanduser(os.path.join('~', '.onepanel', 'credentials'))
        credentials.read(filename)

        try:
            self.account_uid = credentials.get('onepanel', 'account_uid')
        except configparser.NoSectionError as e:
            self.account_uid = None
        try:
            self.user_uid = credentials.get('onepanel', 'uid')
        except configparser.NoSectionError as e:
            self.user_uid = None
        try:
            self.token = credentials.get('onepanel', 'token')
        except configparser.NoSectionError as e:
            self.token = None

        try:
            self.gitlab_impersonation_token = credentials.get('onepanel', 'gitlab_impersonation_token')
        except configparser.NoSectionError as e:
            self.gitlab_impersonation_token = None

        if self.token:
            self.headers['Authorization'] = 'Bearer {}'.format(self.token)

