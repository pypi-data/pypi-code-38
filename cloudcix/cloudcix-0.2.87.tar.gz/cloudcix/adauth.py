from __future__ import unicode_literals
import logging
from keystoneclient import access
from keystoneclient import exceptions
from keystoneclient import utils
from keystoneclient.auth.identity.v3 import AuthMethod, Auth
from keystoneclient.i18n import _
from oslo_config import cfg

_logger = logging.getLogger(__name__)


class ActiveDirectoryAuthMethod(AuthMethod):

    _method_parameters = ['username', 'password', 'token_id']

    def get_auth_data(self, session, auth, headers, **kwargs):
        auth_data = {'token': {'id': self.token_id},
                     'username': self.username, 'password': self.password}
        return 'ad_auth', auth_data


class ActiveDirectoryAuth(Auth):

    _auth_method_class = ActiveDirectoryAuthMethod

    @utils.positional()
    def __init__(self, auth_url,
                 username=None,
                 password=None,
                 token_id=None,
                 reauthenticate=True):
        super(Auth, self).__init__(auth_url=auth_url,
                                   reauthenticate=reauthenticate)
        self._auth_method = self._auth_method_class(username=username,
                                                    password=password,
                                                    token_id=token_id)
        self.token_id = token_id

    def get_auth_ref(self, session, **kwargs):
        headers = {'Accept': 'application/json'}
        body = {'auth': {'identity': {}}}
        ident = body['auth']['identity']
        rkwargs = {}

        for method in self.auth_methods:
            name, auth_data = method.get_auth_data(session,
                                                   self,
                                                   headers,
                                                   request_kwargs=rkwargs)
            ident.setdefault('methods', []).append(name)
            ident[name] = auth_data

        if not ident:
            raise exceptions.AuthorizationFailure(
                _('Authentication method required (e.g. password)'))

        _logger.debug('Making authentication request to %s', self.token_url)
        try:
            resp = session.post(self.token_url, json=body, headers=headers,
                                authenticated=False, log=False, **rkwargs)
        except exceptions.HTTPError as e:
            try:
                resp = e.response.json()['error']['identity']['ad_auth']
            except (KeyError, ValueError):
                pass
            else:
                self.token_id = resp['token']['id']
            raise e

        try:
            resp_data = resp.json()['token']
        except Exception:
            raise exceptions.InvalidResponse(response=resp)
        return access.AccessInfoV3(resp.headers['X-Subject-Token'],
                                   **resp_data)

    @property
    def auth_methods(self):
        return [self._auth_method]

    @classmethod
    def get_options(cls):
        options = super(Auth, cls).get_options()

        options.extend([
            cfg.StrOpt('username', help="Username"),
            cfg.StrOpt('password', secret=True, help="User's password"),
            cfg.StrOpt('token', help="Dict containing a token id")
        ])

        return options
