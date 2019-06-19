from __future__ import unicode_literals
import logging
from keystoneclient import access
from keystoneclient import exceptions
from keystoneclient import utils
from keystoneclient.auth.identity.v3 import AuthMethod, Auth
from keystoneclient.i18n import _
from oslo_config import cfg

_logger = logging.getLogger(__name__)


class CloudCIXAuthMethod(AuthMethod):

    _method_parameters = ['username', 'password', 'idMember', 'token_id']

    def get_auth_data(self, session, auth, headers, **kwargs):
        if self.token_id:
            auth_data = {'token': {'id': self.token_id}}
        else:
            auth_data = {'name': self.username, 'password': self.password}
        if self.idMember:
            auth_data['domain'] = {'id': self.idMember}
        return 'password', {'user': auth_data}


class CloudCIXAuth(Auth):

    _auth_method_class = CloudCIXAuthMethod

    @utils.positional()
    def __init__(self, auth_url,
                 username=None,
                 password=None,
                 idMember=None,
                 scope=None,
                 token_id=None,
                 reauthenticate=True):
        super(Auth, self).__init__(auth_url=auth_url,
                                   reauthenticate=reauthenticate)
        self._auth_method = self._auth_method_class(username=username,
                                                    password=password,
                                                    token_id=token_id,
                                                    idMember=idMember)
        self.idMember = idMember
        self.scope = scope
        self.members = list()
        self.token_id = None

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

        if self.scope:
            body['auth']['scope'] = self.scope

        _logger.debug('Making authentication request to %s', self.token_url)
        try:
            resp = session.post(self.token_url, json=body, headers=headers,
                                authenticated=False, log=False, **rkwargs)
        except exceptions.HTTPError as e:
            try:
                resp = e.response.json()['error']['identity']['password']
            except (KeyError, ValueError):
                pass
            else:
                self.members = resp['members']
                self.token_id = resp['token']['id']
            raise e

        try:
            resp_data = resp.json()['token']
        except (KeyError, ValueError):
            raise exceptions.InvalidResponse(response=resp)
        else:
            self.members = list()
            self.token_id = None
        return access.AccessInfoV3(resp.headers['X-Subject-Token'],
                                   **resp_data)

    @property
    def additional_auth_required(self):
        return self.token_id and self.members

    @property
    def auth_methods(self):
        return [self._auth_method]

    def select_account(self, idMember):
        assert str(idMember) in [m['idMember'] for m in self.members]
        self.idMember = str(idMember)
        self._auth_method.token_id = self.token_id
        self._auth_method.idMember = str(idMember)

    @classmethod
    def get_options(cls):
        options = super(Auth, cls).get_options()

        options.extend([
            cfg.StrOpt('username', help="Username"),
            cfg.StrOpt('password', secret=True, help="User's password"),
            cfg.StrOpt('idMember', help="User's idMember"),
            cfg.StrOpt('scope', help="Dict containing a scope")
        ])

        return options
