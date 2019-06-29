import os
from typing import Optional

from sqlalchemy import MetaData
from sqlalchemy.orm.session import Session

from jsoncfg.value_mappers import require_string
from peek_plugin_base.PluginCommonEntryHookABC import PluginCommonEntryHookABC
from peek_plugin_base.server.PeekServerPlatformHookABC import PeekServerPlatformHookABC
from peek_plugin_base.storage.DbConnection import DbConnection


class PluginServerEntryHookABC(PluginCommonEntryHookABC):
    def __init__(self, pluginName: str, pluginRootDir: str, platform: PeekServerPlatformHookABC):
        PluginCommonEntryHookABC.__init__(self, pluginName=pluginName, pluginRootDir=pluginRootDir)
        self._platform = platform

    @property
    def platform(self) -> PeekServerPlatformHookABC:
        return self._platform

    def migrateStorageSchema(self, metadata: MetaData) -> None:
        """ Initialise the DB

        :param metadata: the SQLAlchemy metadata for this plugins schema

        """

        relDir = self._packageCfg.config.storage.alembicDir(require_string)
        alembicDir = os.path.join(self.rootDir, relDir)
        if not os.path.isdir(alembicDir): raise NotADirectoryError(alembicDir)

        self._dbConn = DbConnection(
            # Ingore this typing error, it's a bug in pycharm
            dbConnectString=str(self.platform.dbConnectString),
            metadata=metadata,
            alembicDir=alembicDir
        )

        self._dbConn.migrate()

    @property
    def dbSession(self) -> Session:
        """ Database Session

        :return: An instance of the sqlalchemy ORM session

        """
        return self._dbConn.ormSession()

    @property
    def publishedServerApi(self) -> Optional[object]:
        """ Published Server API

        :return  class that implements the API that can be used by other PLUGINs on this
        platform.
        """
        return None
