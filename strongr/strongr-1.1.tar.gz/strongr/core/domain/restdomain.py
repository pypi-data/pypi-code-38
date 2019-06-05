import dependency_injector.containers as containers
import dependency_injector.providers as providers

from strongr.restdomain.service import Oauth2Service
from strongr.restdomain.factory.oauth2 import CommandFactory as Oauth2CommandFactory,\
                                                QueryFactory as Oauth2QueryFactory


class RestDomain(containers.DeclarativeContainer):
    """IoC container"""
    oauth2CommandFactory = providers.Singleton(Oauth2CommandFactory)
    oauth2QueryFactory = providers.Singleton(Oauth2QueryFactory)
    oauth2Service = providers.Singleton(Oauth2Service)
