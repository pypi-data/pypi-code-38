# -*- coding: utf-8 -*-
"""\
When used in conjunction with the `Pyramid Web Framework
<http://docs.pylonsproject.org/projects/pyramid/en/latest/>`_
this module will setup the cnx-db library within the Pyramid application.

For usage examples, see :ref:`pyramid_usage`

"""
from sqlalchemy import MetaData
from zope.interface import Interface

from cnxdb.scripting import prepare


__all__ = ('includeme', 'meta',)


meta = MetaData()


class _Tables(object):

    metadata = None

    def __init__(self, metadata=meta):
        self.metadata = metadata

    def __getattr__(self, name):
        try:
            return self.metadata.tables[name]
        except KeyError:
            raise AttributeError(name)


class IEngine(Interface):
    """A SQLAlchemy Engine"""


class ITables(Interface):
    """Object with attribute access to SQLAlchemy defined tables.
    Each attribute maps to the name of the database table.

    """


def get_db_engine(request, name='common'):
    return request.registry.getUtility(IEngine, name=name)


def db_tables(request):
    return request.registry.getUtility(ITables)


def includeme(config):
    """Used by pyramid to include this package.

    This sets up a dictionary of engines for use
    and the a ``tables`` object
    containing the defined database tables
    as sqlalchemy ``Table`` objects.
    They can be retrieved via the registry
    at ``registry.engines`` and ``registry.tables``.

    """
    env = prepare(config.registry.settings)
    engines = env['engines']

    # Initialize the tables on the registry
    tables = _Tables()
    tables.metadata.reflect(bind=engines['common'])
    config.registry.registerUtility(tables, ITables)

    # Register engine utilities
    for name, engine in engines.items():
        config.registry.registerUtility(engine, IEngine, name=name)
    # ... and register the 'common' engine as an unnamed utility
    config.registry.registerUtility(engines['common'], IEngine)

    # Create request methods
    config.add_request_method(get_db_engine)
    config.add_request_method(db_tables, reify=True)
