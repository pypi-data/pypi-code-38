from rockset import Client
from .command import Command

class AuthCommand(Command):
    def __init__(self, *args, **kwargs):
        super(AuthCommand, self).__init__(*args, **kwargs)
        (creds, profile) = self.require_creds()
        self.client = Client(api_key=self.api_key, api_server=self.api_server)
        self.logger.info('client successfully created')
        self.logger.info('using apiserver host: {}'.format(
            self.client.api_server))
        if self.verbose >= 2:
            self.client._apicall = self.client.call_api
            self.client.call_api = self._apicall
        return
