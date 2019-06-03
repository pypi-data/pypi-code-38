from abc import ABC, abstractmethod
from functools import partial
from uuid import UUID

from .. import Base
from ..infrastructure import InfrastructureFactory
from ..repository import RepositoryFactory
from .events import Event, EventService, event

__all__ = ["event", "Event", "EventService"]


class CommandBase(Base, ABC):
    __slots__ = ["repository_factory", "context", "user_uuid"]

    def __init__(
        self,
        repository_factory: RepositoryFactory,
        context: str,
        user_uuid: UUID,
        event_service: EventService,
    ):
        self.repository_factory = repository_factory
        self.context = context
        self.user_uuid = user_uuid
        self.event_service = event_service

    def get_repository(self, name):
        """Initialize and retrieve a repository by name.

        This also passes the event service to the repository constructor.

        :param name: Name of the repository to retrieve
        :type name: str
        :return: Initialized repository
        :rtype: RepositoryBase
        """

        return self.repository_factory.get_repository(
            name=name, context=self.context, event_service=self.event_service
        )


class QueryBase(Base, ABC):
    __slots__ = ["repository_factory", "context", "user_uuid"]

    def __init__(self, repository_factory, context, user_uuid: UUID):
        self.repository_factory = repository_factory
        self.context = context
        self.user_uuid = user_uuid

    def get_repository(self, name):
        """Initialize and retrieve a repository by name.

        Passes None as the `event_service`, so any calls to state-changing
        commands can raise the right exceptions.

        :param name: Name of the repository to retrieve
        :type name: str
        :return: Initialized repository
        :rtype: RepositoryBase
        """

        return self.repository_factory.get_repository(
            name=name, context=self.context, event_service=None
        )


class QueryMiddleware(Base, ABC):
    __slots__ = [
        "infrastructure_factory",
        "correlation_id",
        "domain",
        "context",
        "user_uuid",
    ]

    def __init__(
        self,
        infrastructure_factory: InfrastructureFactory,
        correlation_id: UUID,
        domain: str,
        context: str,
        user_uuid: UUID,
    ):
        """Initialize the middleware with an infrastructure factory and some
        parameters from the current request.

        :param infrastructure_factory: [description]
        :type infrastructure_factory: InfrastructureFactory
        :param correlation_id: Unique identifier for the current "chain of
            events"
        :type correlation_id: UUID
        :param domain: Domain the command is a part of
        :type domain: str
        :param context: Context the command is being executed in
        :type context: str
        :param user_uuid: UUID of the user executing the command
        :type user_uuid: UUID
        """

        self.infrastructure_factory = infrastructure_factory
        self.correlation_id = correlation_id
        self.domain = domain
        self.context = context
        self.user_uuid = user_uuid

    @abstractmethod
    def __call__(self, func):
        """Call the specified function.

        Override this method (including the defined params) in your middleware
        class. The logic or functionality you want to implement should go
        before and after your call to `func()`.

        Remember to return whatever `func()` returns!

        :param func: function to execute
        :type func: partial function
        """
        pass


class MiddlewareBase(Base, ABC):
    __slots__ = [
        "infrastructure_factory",
        "event_service",
        "correlation_id",
        "domain",
        "context",
        "user_uuid",
    ]

    def __init__(
        self,
        infrastructure_factory: InfrastructureFactory,
        event_service: EventService,
        correlation_id: UUID,
        domain: str,
        context: str,
        user_uuid: UUID,
    ):
        """Initialize the middleware with an infrastructure factory and some
        parameters from the current request.

        :param infrastructure_factory: Infrastructure factory to use
        :type infrastructure_factory: InfrastructureFactory
        :param event_service: Event service instance to use
        :type event_service: EventService
        :param correlation_id: Unique identifier for the current "chain of
            events"
        :type correlation_id: UUID
        :param domain: Domain the command is a part of
        :type domain: str
        :param context: Context the command is being executed in
        :type context: str
        :param user_uuid: UUID of the user executing the command
        :type user_uuid: UUID
        """

        self.infrastructure_factory = infrastructure_factory
        self.event_service = event_service
        self.correlation_id = correlation_id
        self.domain = domain
        self.context = context
        self.user_uuid = user_uuid

    @abstractmethod
    def __call__(self, func):
        """Call instantiated class.

        Override this method (including the defined params) in your middleware
        class. The logic or functionality you want to implement should go
        before and after your call to `func()`.

        :param func: function to execute
        :type func: partial function
        """
        pass


class CommandInfrastructureCleanup(MiddlewareBase):
    """Set current event in infrastructure factory and clear it after the event is finished."""

    def __call__(self, func):
        try:
            func()
        finally:
            self.infrastructure_factory.flush_local_storage()


class QueryInfrastructureCleanup(QueryMiddleware):
    """Set current event in infrastructure factory and clear it after the query is finished."""

    def __call__(self, func):
        try:
            rv = func()
            return rv
        finally:
            self.infrastructure_factory.flush_local_storage()


class QueryWrapper(Base):
    """Wrapper class for query instances that applies middleware."""

    def __init__(self, query_instance, middleware: list):
        self.middleware = middleware
        self.query_instance = query_instance

    def __getattr__(self, attr):
        """Get an attribute on the wrapped class, wrapped by "event" code.

        This event code ensures the command can't return anything, and creates
        an Event instance.

        :param attr: attribute to retrieve
        :type attr: str
        :return: wrapped method
        :rtype: callable
        """
        original_attribute = self.query_instance.__getattribute__(attr)
        if callable(original_attribute):

            def wrapped(*args, **kwargs):
                """Return attribute wrapped in middlewares."""

                with self.statsd.get_timer("TotalQueryTime").time(attr):
                    wrapped_func = partial(original_attribute, *args, **kwargs)

                    for middleware in self.middleware:
                        wrapped_func = partial(middleware, func=wrapped_func)
                    return wrapped_func()

            return wrapped
        else:
            return original_attribute


class CommandWrapper(Base):
    """Wrapper class for command instances. Handles creation of Events."""

    def __init__(self, command_instance):
        self.command_instance = command_instance
        self.middlewares = []

    def register_middleware(self, middleware: MiddlewareBase):
        """Register middleware to be wrapped around command.

        From inner to outer layer, the last middleware class to get registered will be
        the outer shell and will be executed first and last.

        :param middleware: middleware to register
        :type middleware: MiddlewareBase
        """
        self.middlewares.append(middleware)

    def __getattr__(self, attr):
        """Get an attribute on the wrapped class, wrapped by "event" code.

        This event code ensures the command can't return anything, and creates
        an Event instance.

        :param attr: attribute to retrieve
        :type attr: str
        :return: wrapped method
        :rtype: callable
        """

        original_attribute = self.command_instance.__getattribute__(attr)
        if callable(original_attribute):

            def wrapped(*args, **kwargs):
                """Return attribute wrapped in middlewares."""
                with self.statsd.get_timer("TotalCommandTime").time(attr):

                    wrapped_func = partial(original_attribute, **kwargs)
                    for middleware in self.middlewares:
                        wrapped_func = partial(middleware, func=wrapped_func)

                    wrapped_func()
                return

            return wrapped
        else:
            return original_attribute


class CQRS(Base):
    """Keep commands and queries separated.

    CQRS: Command Query Responsibility Separation
    """

    __slots__ = [
        "domains",
        "infrastructure_factory",
        "command_wrapper_middleware",
        "query_middleware",
    ]

    def __init__(
        self,
        domains,
        infrastructure_factory: InfrastructureFactory,
        command_wrapper_middleware=None,
        query_middleware=None,
    ):
        """Create a new CQRS instance from a list of domains.

        :param domains: iterable returning domains. Domains are classes or
            packages with at least a "REQUIRED_REPOSITORIES" variable defining
            which repositories are necessary to use the domain.
        :type domains: object
        :param infrastructure_factory: Infrastructure factory, created with
            the required configuration, that the repositories can use to
            create infrastructure instances.
        :type infrastructure_factory: InfrastructureFactory
        :param command_wrapper_middleware: Middlewares to be wrapped around
            command.
        :type command_wrapper_middleware: list of MiddlewareBase
        """
        self.domains = {}

        if command_wrapper_middleware is None:
            command_wrapper_middleware = []

        if query_middleware is None:
            query_middleware = []

        self.command_wrapper_middleware = command_wrapper_middleware
        self.query_middleware = query_middleware
        self.infrastructure_factory = infrastructure_factory

        for domain in domains:
            repo_factory = RepositoryFactory(infrastructure_factory)

            for name, repo in domain.REQUIRED_REPOSITORIES.items():
                repo_factory.register_repository(name=name, repository=repo)

                for name, infra in repo.REQUIRED_INFRASTRUCTURE.items():
                    infrastructure_factory.register_infrastructure(
                        name=name, infrastructure=infra
                    )

            self.domains[domain.__name__] = {
                "module": domain,
                "repository_factory": repo_factory,
            }

    def get_query_instance(
        self, correlation_id: UUID, domain: str, context, user_uuid: UUID
    ):
        """Instantiate and return the "query" part of the specified domain.

        :param domain: name of the domain to get the query instance for
        :type domain: str
        :param context: context for this query instance
        :type context: str
        :param user_uuid: UUID of the user that's going to execute commands
        :type user_uuid: uuid
        """

        self.logger.debug(
            f"Creating query instance for domain '{domain}' with context "
            + f"'{context}' for user '{user_uuid}'"
        )

        with self.statsd.get_timer(domain).time("get_query_instance"):
            query_instance = self.domains[domain]["module"].get_query_instance(
                self.domains[domain]["repository_factory"],
                context=context,
                user_uuid=user_uuid,
            )

            initialized_middleware = []

            # Outermost layer: cleanup infrastructure when we're done
            for mw in [*self.query_middleware, QueryInfrastructureCleanup]:
                initialized_middleware.append(
                    mw(
                        infrastructure_factory=self.infrastructure_factory,
                        correlation_id=correlation_id,
                        domain=domain,
                        context=context,
                        user_uuid=user_uuid,
                    )
                )

            wrapped_query = QueryWrapper(
                query_instance=query_instance,
                middleware=initialized_middleware,
            )

        return wrapped_query

    def get_command_instance(
        self, correlation_id: UUID, domain: str, context, user_uuid: UUID
    ):
        """Instantiate and return the "command" instance of the specified domain.

        Command instance is instantiated with optional layers of middleware to handle
        various functions when executing a command. `InfrastructureStateManager` is
        always registered as the outermost layer.

        :param correlation_id: unique identifier for the current chain of
            events.
        :param domain: name of the domain to get the query instance for
        :type domain: str
        :param context: context for this command instance
        :type context: str
        :param user_uuid: UUID of the user that's going to execute commands
        :type user_uuid: uuid
        """
        self.logger.debug(
            f"Creating command instance for domain '{domain}' with context "
            + f"'{context}' for user '{user_uuid}'"
        )

        with self.statsd.get_timer(domain).time("get_command_instance"):
            event_service = EventService(
                correlation_id=correlation_id,
                domain=domain,
                context=context,
                user_uuid=user_uuid,
            )

            cmd_instance = self.domains[domain]["module"].get_command_instance(
                self.domains[domain]["repository_factory"],
                context=context,
                user_uuid=user_uuid,
                event_service=event_service,
            )

            cmd_wrapped = CommandWrapper(command_instance=cmd_instance)

            # Always "outer layer" to clean up infrastructure
            for middleware in [
                *self.command_wrapper_middleware,
                CommandInfrastructureCleanup,
            ]:
                initialized_middleware = middleware(
                    infrastructure_factory=self.infrastructure_factory,
                    correlation_id=correlation_id,
                    domain=domain,
                    context=context,
                    user_uuid=user_uuid,
                    event_service=event_service,
                )
                cmd_wrapped.register_middleware(initialized_middleware)

        return cmd_wrapped
