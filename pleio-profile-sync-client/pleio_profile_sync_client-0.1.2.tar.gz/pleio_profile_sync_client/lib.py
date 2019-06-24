import json
from urllib.parse import urljoin
import requests

LIMIT = 500


class Client:
    def __init__(self, base_url, api_secret, read_only=False, verbose=False):
        self.base_url = base_url
        self.api_secret = api_secret
        self.read_only = read_only
        self.verbose = verbose

        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': 'Bearer {}'.format(self.api_secret)
        })

    def get_users(self):
        offset = 0

        while True:
            url = urljoin(self.base_url, 'users?limit={}&offset={}'.format(LIMIT, offset))
            data = self.session.get(url).json()
            for user in data['users']:
                yield user

            offset += LIMIT
            if offset > data['total']:
                break

    def post_user(self, data):
        if self.read_only:
            return False

        url = urljoin(self.base_url, 'users')
        result = self.session.post(url, data=json.dumps(data)).json()

        if self.verbose:
            print(result)

        return result

    def ban_user(self, guid):
        if self.read_only:
            return False

        url = urljoin(self.base_url, 'users/{}/ban'.format(guid))
        result = self.session.post(url).json()

        if self.verbose:
            print(result)

        return result

    def unban_user(self, guid):
        if self.read_only:
            return False

        url = urljoin(self.base_url, 'users/{}/unban'.format(guid))
        result = self.session.post(url).json()

        if self.verbose:
            print(result)

        return result

    def post_avatar(self, guid, avatar):
        url = urljoin(self.base_url, 'users/{}/avatar'.format(guid))
        result = self.session.post(url, files={
            'avatar': avatar
        }).json()

        if self.verbose:
            print(result)

        return result