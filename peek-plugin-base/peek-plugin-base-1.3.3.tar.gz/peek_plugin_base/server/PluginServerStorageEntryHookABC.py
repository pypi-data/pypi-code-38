import os
from abc import ABCMeta, abstractproperty
from typing import Optional, Callable

from jsoncfg.value_mappers import require_string
from sqlalchemy import MetaData
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm.session import Session
from twisted.internet.defer import Deferred

from peek_plugin_base.storage.DbConnection import DbConnection, DbSessionCreator


class PluginServerStorageEntryHookABC(metaclass=ABCMeta):
    def _migrateStorageSchema(self, metadata: MetaData) -> None:
        """ Initialise the DB

        This method is called by the platform between the load() and start() calls.
        There should be no need for a plugin to call this method it's self.

        :param metadata: the SQLAlchemy metadata for this plugins schema

        """

        relDir = self._packageCfg.config.storage.alembicDir(require_string)
        alembicDir = os.path.join(self.rootDir, relDir)
        if not os.path.isdir(alembicDir): raise NotADirectoryError(alembicDir)

        self._dbConn = DbConnection(
            dbConnectString=self.platform.dbConnectString,
            metadata=metadata,
            alembicDir=alembicDir,
            enableCreateAll=False
        )

        self._dbConn.migrate()

    @property
    def dbSessionCreator(self) -> DbSessionCreator:
        """ Database Session

        This is a helper property that can be used by the papp to get easy access to
        the SQLAlchemy C{Session}

        :return: An instance of the sqlalchemy ORM session

        """
        return self._dbConn.ormSessionCreator

    @property
    def dbEngine(self) -> Engine:
        """ DB Engine

        This is a helper property that can be used by the papp to get easy access to
        the SQLAlchemy C{Engine}

        :return: The instance of the database engine for this plugin

        """
        return self._dbConn._dbEngine

    def prefetchDeclarativeIds(self, Declarative, count) -> Deferred:
        """ Get PG Sequence Generator

        A PostGreSQL sequence generator returns a chunk of IDs for the given
        declarative.

        :return: A generator that will provide the IDs
        :rtype: an iterator, yielding the numbers to assign

        """
        return self._dbConn.prefetchDeclarativeIds(Declarative=Declarative, count=count)

    @abstractproperty
    def dbMetadata(self) -> MetaData:
        """ DB Metadata

        This property returns an instance to the metadata from the ORM Declarative
         on which, all the ORM classes have inherited.

        This means the metadata knows about all the tables.

        NOTE: The plugin must be constructed with a schema matching the plugin package

        :return: The instance of the metadata for this plugin.

        Example from peek_plugin_noop.storage.DeclarativeBase.py
        --------------------------------------------------------

        ::

            metadata = MetaData(schema="noop")
            DeclarativeBase = declarative_base(metadata=metadata)

        """
        pass
