"""Provides functional access to the UnityCloud Core service.
"""
from datetime import datetime, timedelta
from logging import getLogger
from collabi.open_struct import OpenStruct

class Core(object):
    class User(OpenStruct):
        def __init__(self, rest, auth):
            self._rest = rest
            self._auth = auth
            resp = self._rest.request('get', 'users/me', auth=self._auth)
            self.as_json = resp.json()
            super(Core.User, self).__init__(self.as_json)

        def orgs(self, include_archived=False):
            resp = self._rest.request('get', 'orgs', auth=self._auth)
            return resp.json()['orgs']

        def projects(self, org_id=None, include_archived=False):
            fk = self.foreign_key
            path = 'orgs/'+org_id if org_id else 'users/'+fk
            resp = self._rest.request('get', path+'/projects', auth=self._auth)
            projects = resp.json()['projects']
            if include_archived:
                return projects
            else:
                return [p for p in projects if p['archived'] == False]

        def project(self, project_id):
            path = 'projects/'+project_id
            resp = self._rest.request('get', path, auth=self._auth)
            return resp.json()

    def __init__(self, rest, access_token=None, refresh_token=None, expiry=None,
                 save_auth_callback=None):
        self._logger = getLogger('unity.core')
        self._rest = rest
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._expiry = expiry
        self._save_auth_callback = save_auth_callback

    def login(self, email, password):
        login = {
            'grant_type': 'password',
            'username': email,
            'password': password
        }
        self._save_auth(self._rest.request('post', 'login', json=login))

    def get_authorization_header(self):
        if self._access_token:
            self.refresh()
            return 'Bearer '+self._access_token
        return None

    def refresh(self):
        if not self._refresh_token or not self._expiry:
            raise LookupError('Need to authorize: no refresh token provided')
        now = datetime.utcnow()
        if now < self._expiry:
            return
        self._logger.debug('Refreshing access token (%s < %s)' % (str(now), str(self._expiry)))
        refresh = {
            'grant_type': 'refresh_token',
            'refresh_token': self._refresh_token
        }
        self._save_auth(self._rest.request('post', 'login/refresh', json=refresh))

    def current_user(self, auth):
        if not hasattr(self, '_current_user'):
            self._current_user = Core.User(self._rest, auth)
        return self._current_user

    def _save_auth(self, resp):
        json = resp.json()
        self._access_token = json['access_token']
        self._refresh_token = json['refresh_token']
        expires_in = int(json['expires_in']) - 30 # fudge factor for transit latency
        self._expiry = datetime.utcnow() + timedelta(seconds=expires_in)
        self._logger.info('Access token from ' + resp.url + ': ' + self._access_token)
        if self._save_auth_callback:
            self._save_auth_callback(self._access_token, self._refresh_token, self._expiry)
