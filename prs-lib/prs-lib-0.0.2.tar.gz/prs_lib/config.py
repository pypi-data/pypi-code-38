from . import validator

__all__ = ['PRSConfig']

HOST_DEV = 'https://dev.press.one'
HOST_BETA = 'https://beta.press.one'
HOST_RELEASE = 'https://press.one'


class PRSConfig:
    def __init__(self, options):
        """
        options: {
            'dev': str,
            'debug': bool,
            'private_key': str,
            'token': str,
            'address': str
        }
        """
        if not options:
            return
        self.env = options.get('env', 'prod')
        self.debug = options.get('debug', False)
        self.private_key = options.get('private_key', None)
        self.token = options.get('token', None)
        self.address = options.get('address', None)
        if self.env == 'dev':
            self.host = HOST_DEV
        elif self.env == 'beta':
            self.host = HOST_BETA
        elif self.env == 'prod':
            self.host = HOST_RELEASE
        else:
            raise ValueError('supported env: dev or beta or prod')

    def get_host(self):
        """get host url"""
        return self.host

    def get_auth_opts(self):
        """get auth opts"""
        private_key = self.private_key
        token = self.token
        validator.assert_exc(
            private_key or token,
            'config.private_key or config.token cannot be null'
        )
        auth_opts = {
            'private_key': private_key,
            'token': token,
        }
        return auth_opts
