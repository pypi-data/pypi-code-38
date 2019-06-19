import json
import os

import requests

try:
    from urllib.parse import unquote, quote_plus, urljoin
except ImportError:  # Python 2
    # noinspection PyUnresolvedReferences
    from urllib import unquote, quote_plus
    # noinspection PyUnresolvedReferences
    from urlparse import urljoin


class VedavaapiSession(object):
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/') + '/'
        self.session = requests.Session()
        self.access_token = None

        self.accounts_authentication_done = False

    def abs_url(self, url_part):
        return os.path.join(
            self.base_url,
            url_part.lstrip('/')
        )

    def _authenticate(self, email, password):
        if self.accounts_authentication_done:
            return True
        if not email or not password:
            return False

        r = self.post("accounts/v1/oauth/signin", {'email': email, 'password': password})
        if r.status_code != 200:
            print("Authentication failed.", r.json())
            return False

        self.accounts_authentication_done = True
        return True

    def _register_client(self):
        myclients = self.get('accounts/v1/oauth/clients').json()
        myclients = [m for m in myclients if 'client_credentials' in m['grant_types']]
        if myclients:
            self.client_json = myclients[0]
        else:
            new_client_post_data = {
                "name": 'test_client',
                "grant_types": '["client_credentials"]',
                "client_type": 'private',
                "return_projection": '{"permissions": 0}',
            }

            resp = self.post('accounts/v1/oauth/clients', data=new_client_post_data)
            resp.raise_for_status()
            self.client_json = resp.json()

    def _authorize_through_client_credentials_grant(self, client_id, client_secret):
        request_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials"
        }
        atr = self.post('accounts/v1/oauth/token', data=request_data)
        atr.raise_for_status()
        self.access_token = atr.json()['access_token']

    def set_access_token(self, access_token):
        self.access_token = access_token

    def signin(self, email, password):
        self._authenticate(email, password)
        self._register_client()
        self._authorize_through_client_credentials_grant(self.client_json['client_id'], self.client_json['client_secret'])
        print(self.access_token)

    @classmethod
    def authorization_header(cls, access_token):
        return 'Bearer {}'.format(access_token) if access_token else None

    @classmethod
    def authorized_headers(cls, headers, access_token):
        if not access_token:
            return
        new_headers = headers.copy()
        new_headers['Authorization'] = cls.authorization_header(access_token)
        return new_headers

    def set_access_token_from_file(self, file_path):
        creds = json.loads(open(file_path, 'rb').read().decode('utf-8'))
        access_token = creds['access_token']
        self.set_access_token(access_token)

    def get(self, url, parms=None, authorize_request=True, **kwargs):
        url = self.abs_url(url)
        parms = parms or {}
        headers = kwargs.pop('headers', {})
        if authorize_request:
            headers = self.authorized_headers(headers, self.access_token)

        print("{} {}".format("GET", url))
        r = self.session.get(url, params=parms, headers=headers, **kwargs)
        return r

    def post(self, url, data=None, files=None, authorize_request=True, **kwargs):
        url = self.abs_url(url)
        data = data or {}
        headers = kwargs.get('headers', {})
        if authorize_request:
            headers = self.authorized_headers(headers, self.access_token)

        print("{} {}".format("POST", url))
        r = self.session.post(url, data=data, files=files, headers=headers, **kwargs)
        return r

    def put(self, url, data=None, files=None, authorize_request=True, **kwargs):
        url = self.abs_url(url)
        data = data or {}
        headers = kwargs.get('headers', {})
        if authorize_request:
            headers = self.authorized_headers(headers, self.access_token)

        print("{} {}".format("PUT", url))
        r = self.session.put(url, data=data, files=files, headers=headers, **kwargs)
        return r

    def delete(self, url, data=None, authorize_request=True, **kwargs):
        url = self.abs_url(url)
        data = data or {}
        headers = kwargs.get('headers', {})
        if authorize_request:
            headers = self.authorized_headers(headers, self.access_token)

        print("{} {}".format("DELETE", url))
        r = self.session.delete(url, data=data, headers=headers, **kwargs)
        return r

def is_success(resp):
    return resp.status_code == 200


class ObjModelException(BaseException):

    def __init__(self, message, status_code=None, attachments=None):
        super(ObjModelException, self).__init__(message)
        self.message = message
        self.status_code = status_code
        self.attachments = attachments


from . import accounts, objstore, iiif_import_helper
