from strongr.core.abstracts.abstractservice import AbstractService

from strongr.secretsdomain.command import AddSecret, RemoveSecret
from strongr.secretsdomain.handler import AddSecretHandler, RemoveSecretHandler

from strongr.secretsdomain.query import GetSecret, ListSecrets
from strongr.secretsdomain.handler import GetSecretHandler, ListSecretsHandler

class SecretService(AbstractService):
    _command_bus = None
    _query_bus = None

    def register_models(self):
        from strongr.secretsdomain.model import Secret
        # importing alone is enough for registration

    def get_command_bus(self):
        if self._command_bus is None:
            self._command_bus = self._make_default_commandbus({
                        AddSecretHandler: AddSecret,
                        RemoveSecretHandler: RemoveSecret
                    })
        return self._command_bus

    def get_query_bus(self):
        if self._query_bus is None:
            self._query_bus = self._make_default_querybus({
                    GetSecretHandler: GetSecret,
                    ListSecretsHandler: ListSecrets
                })
        return self._query_bus
