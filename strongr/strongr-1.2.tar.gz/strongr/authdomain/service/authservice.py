from strongr.core.abstracts.abstractservice import AbstractService

from strongr.authdomain.query import IsValidUser
from strongr.authdomain.handler import IsValidUserHandler

class AuthService(AbstractService):
    _command_bus = None
    _query_bus = None

    def getCommandBus(self):
        if self._command_bus is None:
            self._command_bus = self._make_default_commandbus({
                    })
        return self._command_bus

    def getQueryBus(self):
        if self._query_bus is None:
            self._query_bus = self._make_default_querybus({
                    IsValidUserHandler: IsValidUser,
                })
        return self._query_bus
