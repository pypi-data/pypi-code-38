import dependency_injector.containers as containers
import dependency_injector.providers as providers

from strongr.authdomain.service import AuthService
from strongr.authdomain.factory import QueryFactory

class AuthDomain(containers.DeclarativeContainer):
    """IoC container of service providers."""
    authService = providers.Singleton(AuthService)
    commandFactory = providers.Singleton(lambda: None)
    queryFactory = providers.Singleton(QueryFactory)
