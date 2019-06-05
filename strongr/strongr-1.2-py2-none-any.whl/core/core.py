import dependency_injector.containers as containers
import dependency_injector.providers as providers

from .eventspublisher import EventsPublisher
from strongr.core.middlewares.celery.commandrouter import CommandRouter

class Core(containers.DeclarativeContainer):
    """IoC container of core component providers."""
    config = providers.Configuration('config')

    inter_domain_events_publisher = providers.Singleton(EventsPublisher, 'InterDomain')

    command_router = providers.Singleton(CommandRouter)
