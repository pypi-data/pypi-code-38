import prs_utility as utility

from .request import request
from . import sign_utility
from . import validator

__all__ = ['Dapp', ]


class Dapp:
    def __init__(self, config):
        """
        :param config: PRSConfig
        """
        self.config = config

    def is_name_exist(self, name):
        """
        :param name: str
        """
        validator.assert_exc(name, 'name cannot be null')
        query = {'name': name}
        return request(
            self.config.host,
            method='GET',
            path='/apps/check',
            query=query,
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug,
        )

    def create(self, dapp):
        """
        :param dapp: dict
            {
                'name': str,
                'description': str,
                'redirect_url': str,
                'url': str,
                'logo': str
            }
        """
        keys = ['name', 'description', 'redirect_url', 'url', ]
        validator.check_dict_and_assert('dapp', dapp, keys)
        data = {
            'name': dapp['name'],
            'description': dapp['description'],
            'redirectUrl': dapp['redirect_url'],
            'url': dapp['url'],
        }
        if dapp.get('logo'):
            data['logo'] = dapp['logo']
        return request(
            self.config.host,
            method='POST',
            path='/apps',
            data=data,
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug,
        )

    def update(self, address, dapp):
        """
        :param address: str
        :param dapp: dict
            {
                'name': str,
                'description': str,
                'redirect_url': str,
                'url': str,
                'logo': str
            }
        """
        validator.assert_exc(address, 'address cannot be null')
        keys = ['name', 'description', 'redirect_url', 'url', ]
        validator.check_dict_and_assert('dapp', dapp, keys)
        data = {
            'name': dapp['name'],
            'description': dapp['description'],
            'redirectUrl': dapp['redirect_url'],
            'url': dapp['url'],
        }
        if dapp.get('logo'):
            data['logo'] = dapp['logo']
        return request(
            self.config.host,
            method='PUT',
            path=f'/apps/{address}',
            data=data,
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug,
        )

    def delete(self, address):
        """
        :param address: str
        """
        validator.assert_exc(address, 'address cannot be null')
        return request(
            self.config.host,
            method='DELETE',
            path=f'/apps/{address}',
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug,
        )

    def get_by_address(self, address):
        """
        :param address: str
        """
        validator.assert_exc(address, 'address cannot be null')
        return request(
            self.config.host,
            method='GET',
            path=f'/apps/{address}',
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug,
        )

    def get_dapps(self):
        return request(
            self.config.host,
            method='GET',
            path='/apps',
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug,
        )

    def get_authorize_url(self, address):
        """
        :param address: str, app address
        """
        validator.assert_exc(address, 'address cannot be null')
        return f'{self.config.host}/developer/apps/{address}/authorize'

    def web_authorize(self, app_address):
        """
        :param app_address: str, app address
        """
        validator.assert_exc(app_address, 'app_address cannot be null')
        validator.assert_exc(
            self.config.address, 'config.address cannot be null'
        )
        authorize_opts = {'userAddress': self.config.address}
        auth_opts = self.config.get_auth_opts()
        private_key = auth_opts['private_key']
        token = auth_opts['token']
        if private_key:
            authorize_opts['type'] = 'email'
            res = request(
                self.config.host,
                method='GET',
                path=f'/apps/{app_address}/auth',
                auth_opts=auth_opts
            )
            auth_address = res.json()['authAddress']
            sign = utility.sign_block_data({
                'app_provider': 'press.one',
                'app_address': app_address,
                'auth_address': auth_address,
                'authorized': True,
            }, private_key)
            data = {
                'authAddress': auth_address,
                'signature': sign['signature'],
            }
            request(
                self.config.host,
                method='POST',
                path=f'/apps/{app_address}/auth',
                data=data,
                auth_opts=auth_opts,
                debug=self.config.debug
            )
            authorize_opts['authAddress'] = auth_address
        elif token:
            authorize_opts['type'] = 'phone'
        return request(
            self.config.host,
            method='POST',
            path=f'/apps/{app_address}/authorize',
            data=authorize_opts,
            auth_opts=auth_opts,
            debug=self.config.debug
        )

    def auth_by_code(self, code, app_address, app_private_key):
        """
        :param code: str
        :param app_address: str
        :param app_private_key: str
        """
        validator.assert_exc(code, 'code cannot be null')
        validator.assert_exc(app_address, 'app_address cannot be null')
        validator.assert_exc(app_private_key, 'app_private_key cannot be null')
        auth_opts = {'private_key': app_private_key}
        data = {
            'code': code,
        }
        return request(
            self.config.host,
            method='POST',
            path=f'/apps/{app_address}/authenticate',
            data=data,
            auth_opts=auth_opts,
            debug=self.config.debug
        )

    def authenticate(self, app_address, auth_address):
        """
        :param app_address: str
        :param auth_address: str
        """
        validator.assert_exc(app_address, 'app_address cannot be null')
        auth_opts = self.config.get_auth_opts()
        private_key, token = auth_opts['private_key'], auth_opts['token']
        data = {
            'appAddress': app_address,
        }
        if auth_address:
            block_data = {
                'app_provider': 'press.one',
                'app_address': app_address,
                'auth_address': auth_address,
                'authorized': True,
            }
            sign = None
            if private_key:
                sign = utility.sign_block_data(block_data, private_key)
            elif token:
                res = sign_utility.sign_by_token(
                    block_data, token, self.config.host
                )
                sign = res.json()
            address = utility.sig_to_address(sign['hash'], sign['signature'])
            data.update({
                'userAddress': address,
                'authAddress': auth_address,
                'authorized': True,
                'signature': sign['signature'],
            })
        return request(
            self.config.host,
            method='POST',
            path=f'/apps/{app_address}/authenticate',
            data=data,
            auth_opts=auth_opts,
            debug=self.config.debug
        )

    def deauthenticate(self, app_address, auth_address):
        """
        :param app_address: str
        :param auth_address: str
        """
        validator.assert_exc(app_address, 'app_address cannot be null')
        auth_opts = self.config.get_auth_opts()
        private_key, token = auth_opts['private_key'], auth_opts['token']
        data = {
            'appAddress': app_address,
        }
        if auth_address:
            block_data = {
                'app_provider': 'press.one',
                'app_address': app_address,
                'auth_address': auth_address,
                'authorized': False,
            }
            sign = None
            if private_key:
                sign = utility.sign_block_data(block_data, private_key)
            elif token:
                res = sign_utility.sign_by_token(
                    block_data, token, self.config.host
                )
                sign = res.json()
            address = utility.sig_to_address(sign['hash'], sign['signature'])
            data.update({
                'userAddress': address,
                'authAddress': auth_address,
                'authorized': False,
                'signature': sign['signature'],
            })
        return request(
            self.config.host,
            method='POST',
            path=f'/apps/{app_address}/deauthenticate',
            data=data,
            auth_opts=auth_opts,
            debug=self.config.debug
        )
