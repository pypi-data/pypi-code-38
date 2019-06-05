import dependency_injector.containers as containers
import dependency_injector.providers as providers

from strongr.configdomain.service import ConfigService
from strongr.configdomain.factory import CommandFactory

class ConfigDomain(containers.DeclarativeContainer):
    """IoC container of service providers."""
    configService = providers.Singleton(ConfigService)
    commandFactory = providers.Singleton(CommandFactory)
