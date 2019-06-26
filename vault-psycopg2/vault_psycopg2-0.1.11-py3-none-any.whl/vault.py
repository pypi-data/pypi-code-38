import os
import urllib.request
import threading
import hvac

default_vault_address = os.getenv('VAULT_ADDR', 'http://127.0.0.1:8200')


class Vault:
    vault_server = default_vault_address
    connection_mode = 'token'

    _client = None
    _instance = None
    _lock = threading.Lock()

    parameters = {}

    @classmethod
    def instance(cls, **kwargs):
        if Vault._instance is None:
            with Vault._lock:
                if Vault._instance is None:
                    Vault._instance = Vault(**kwargs)
        return Vault._instance

    def __init__(self, server=default_vault_address, connection_mode='token', client=None, **kwargs):
        self.connection_mode = connection_mode
        self.vault_server = server
        self.parameters = kwargs
        self._client = client

    @property
    def client(self):
        if self._client is not None:
            if self._client.is_authenticated():
                return self._client
            else:
                # noinspection PyBroadException
                try:
                    self._client.close()
                except:
                    pass

        client = hvac.Client(url=self.vault_server)
        if self.connection_mode == 'token':
            client.token = self.parameters['token']
        elif self.connection_mode == 'ec2':
            contents = urllib.request.urlopen('http://169.254.169.254/latest/dynamic/instance-identity/pkcs7')\
                .read() \
                .decode('utf-8') \
                .replace('\n', '')
            client.auth_ec2(contents, nonce=self.parameters['nonce'], role=self.parameters['role'], mount_point='aws')
        else:
            getattr(client, 'auth_' + self.connection_mode)(**self.parameters)

        self._client = client
        return self._client
