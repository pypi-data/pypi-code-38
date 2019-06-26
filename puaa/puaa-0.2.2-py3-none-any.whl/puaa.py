# MIT License
#
# Copyright (c) 2019 Roman Kindruk
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from authlib.flask.oauth2 import AuthorizationServer
from authlib.oauth2.rfc6749 import grants
from authlib.oauth2.rfc6749 import ClientMixin
from authlib.jose import jwt
from authlib.oauth2.rfc6749.util import scope_to_list
from authlib.common.encoding import to_native
import time


class Client(ClientMixin):
    def __init__(self, client_info):
        self.info = client_info

    def __repr__(self):
        return '<Client: {}>'.format(self.info['id'])

    def check_token_endpoint_auth_method(self, method):
        return True

    def check_client_secret(self, client_secret):
        return client_secret == self.info['secret']

    def check_grant_type(self, grant_type):
        grant_types = scope_to_list(self.info['authorized-grant-types'])
        return grant_type in grant_types

    def get_client_id(self):
        return self.info['id']
    
    def _get_permissions(self, permission_type):
        p = self.info[permission_type]
        if p == 'none':
            p = ''
        return p.replace(',', ' ').split()

    def get_scopes(self):
        return self._get_permissions('scope')

    def get_authorities(self):
        return self._get_permissions('authorities')


class ClientCredentialsGrant(grants.ClientCredentialsGrant):
    TOKEN_ENDPOINT_AUTH_METHODS = [
        'client_secret_basic',
        'client_secret_post'
    ]


def _get_private_key(config):
    policy = config['jwt']['token']['policy']
    active_key_id = policy['activeKeyId']
    return policy['keys'][active_key_id]['signingKey']


def _get_permissions(client, permission_type):
    p = client.info[permission_type]
    if p == 'none':
        p = ''
    return p.replace(',', ' ').split()


class PuaaServer(AuthorizationServer):
    def __init__(self, app, config):
        app.config.update(
            OAUTH2_ACCESS_TOKEN_GENERATOR = self.access_token_generator,
            OAUTH2_TOKEN_EXPIRES_IN = {
                'authorization_code': 864000,
                'implicit': 3600,
                'password': 864000,
                'client_credentials': config['jwt']['token']['policy']['accessTokenValiditySeconds']
            }
        )
        super().__init__(app, query_client=self.query_client, save_token=self.save_token)
        self.register_grant(ClientCredentialsGrant)
        self.config.update(config)

    def query_client(self, client_id):
        clients = self.config['oauth']['clients']
        return Client(clients[client_id]) if client_id in clients else None

    def save_token(self, token, request):
        pass

    def access_token_generator(self, client, grant_type, user, scope):
        header = {'alg': 'RS256'}
        now = int(time.time())
        payload = {
            'iss': self.config['issuer']['uri'],
            'sub': client.get_client_id(),
            'zid': client.get_client_id(),
            'iat': now,
            'exp': now + self.config['jwt']['token']['policy']['accessTokenValiditySeconds'],
            'aud': client.get_authorities(),
            'scope': client.get_scopes(),
        }
        key = _get_private_key(self.config)
        s = jwt.encode(header, payload, key)
        return to_native(s)
