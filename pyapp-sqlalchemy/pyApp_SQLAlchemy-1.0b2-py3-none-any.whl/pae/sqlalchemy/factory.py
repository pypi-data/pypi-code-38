from typing import cast

from pyapp.checks import Error
from pyapp.conf.helpers import NamedSingletonFactory, DefaultCache
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Connection, Engine
from sqlalchemy.orm import sessionmaker, Session

__all__ = (
    "engine_factory",
    "get_engine",
    "get_connection",
    "get_raw_connection",
    "get_session",
    "Connection",
    "Session",
)


class EngineFactory(NamedSingletonFactory[Engine]):
    """
    Factory that creates SQLAlchemy engine instances from configuration.
    """

    required_keys = ("url",)
    optional_keys = (
        "connect_args",
        "echo",
        "echo_pool",
        "isolation_level",
        "pool_size",
        "pool_recycle",
        "pool_timeout",
        "strategy",
    )

    def create(self, name: str = None) -> Engine:
        """
        Obtain an engine
        """
        config = self.get(name)
        engine = create_engine(config.pop("url"), **config)
        return engine

    def check_definition(self, config_definitions, name, **_):
        messages = super().check_definition(config_definitions, name)

        # If any serious messages are defined then connection check is likely to fail.
        if any(m.is_serious() for m in messages):
            return messages

        # Open connection to server to check connectivity
        try:
            engine = self.create(name)
            engine.connect()
        except Exception as ex:
            # Catch any error and return an Error
            return Error(
                u"Database connection check failed.",
                u"Check connection parameters, exception raised: {}".format(ex),
                u"settings.{}[{}]".format(self.setting, name),
            )

        return messages


engine_factory = EngineFactory("DATABASE_ENGINES")
get_engine = engine_factory.create


def get_connection(name: str = None) -> Connection:
    """
    Obtain a DBAPI connection.

    :param name: Name of the configuration entry.

    """
    return get_engine(name).connect()


def get_raw_connection(name: str = None):
    """
    Obtain a DBAPI connection.

    :param name: Name of the configuration entry.

    """
    return get_engine(name).raw_connection()


class SessionFactory:
    """
    Factory that generates a SQLAlchemy session from configuration.
    """

    def __init__(self, engine_factory_: EngineFactory = None):
        self.engine_factory = engine_factory_ or engine_factory
        self.session_maker_cache = DefaultCache(self._session_maker_factory)

    def create(self, name: str = None, bind: Connection = None) -> Session:
        """
        Obtain a session.

        Note this applications default behaviour is to require explicit transactions.

        :param name: Name of the configuration entry.
        :param bind: Bind to an existing connection.

        """
        kwargs = {}
        if bind:
            kwargs["bind"] = bind
        return self.session_maker_cache[name](**kwargs)

    def _session_maker_factory(self, name: str) -> Session:
        engine = self.engine_factory.create(name)
        session = sessionmaker(bind=engine, autocommit=True)
        return cast(Session, session)


session_factory = SessionFactory()
get_session = session_factory.create
