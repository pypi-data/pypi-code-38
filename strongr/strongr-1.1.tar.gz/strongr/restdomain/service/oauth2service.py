from strongr.core.abstracts.abstractservice import AbstractService

from strongr.restdomain.command.oauth2 import AppendGrant
from strongr.restdomain.handler.oauth2 import AppendGrantHandler

from strongr.restdomain.query.oauth2 import RetrieveClient, RetrieveGrant,\
                                            RetrieveTokenByAccessToken, RetrieveTokenByRefreshToken
from strongr.restdomain.handler.oauth2 import RetrieveClientHandler, RetrieveGrantHandler,\
                                        RetrieveTokenByAccessTokenHandler, RetrieveTokenByRefreshTokenHandler


class Oauth2Service(AbstractService):
    _command_bus = None
    _query_bus = None

    def register_models(self):
        import strongr.restdomain.model.oauth2
        # importing alone is enough for registration

    def getCommandBus(self):
        if self._command_bus is None:
            self._command_bus = self._make_default_commandbus({
                    AppendGrantHandler: AppendGrant,
                    })
        return self._command_bus

    def getQueryBus(self):
        if self._query_bus is None:
            self._query_bus = self._make_default_querybus({
                    RetrieveClientHandler: RetrieveClient,
                    RetrieveGrantHandler: RetrieveGrant,
                    RetrieveTokenByAccessTokenHandler: RetrieveTokenByAccessToken,
                    RetrieveTokenByRefreshTokenHandler: RetrieveTokenByRefreshToken
                })
        return self._query_bus
