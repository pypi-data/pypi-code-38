import dependency_injector.containers as containers
import dependency_injector.providers as providers

from strongr.secretsdomain.service import SecretService

import dependency_injector.providers as providers

from strongr.secretsdomain.service import SecretService
from strongr.secretsdomain.factory import CommandFactory, QueryFactory

import strongr.core.domain.clouddomain


class SecretDomain(containers.DeclarativeContainer):
    """IoC container of service providers."""
    secret_service = providers.Singleton(SecretService)
    command_factory = providers.Singleton(CommandFactory)
    query_factory = providers.Singleton(QueryFactory)
