import logging
import os

from jsoncfg.value_mappers import require_string
from peek_plugin_base.server.PluginServerEntryHookABC import PluginServerEntryHookABC
from peek_plugin_base.server.PluginServerStorageEntryHookABC import \
    PluginServerStorageEntryHookABC
from peek_plugin_base.storage.DbConnection import DbConnection
from sqlalchemy import MetaData

from peek_plugin_diagram_generic_menu._private.storage import DeclarativeBase
from peek_plugin_diagram_generic_menu._private.storage.DeclarativeBase import \
    loadStorageTuples
from peek_plugin_diagram_generic_menu._private.tuples import loadPrivateTuples
from peek_plugin_diagram_generic_menu.tuples import loadPublicTuples
from .DiagramGenericMenuApi import DiagramGenericMenuApi
from .TupleActionProcessor import makeTupleActionProcessorHandler
from .TupleDataObservable import makeTupleDataObservableHandler
from .admin_backend import makeAdminBackendHandlers
from .controller.MainController import MainController

logger = logging.getLogger(__name__)


class ServerEntryHook(PluginServerEntryHookABC, PluginServerStorageEntryHookABC):
    def __init__(self, *args, **kwargs):
        """" Constructor """
        # Call the base classes constructor
        PluginServerEntryHookABC.__init__(self, *args, **kwargs)

        #: Loaded Objects, This is a list of all objects created when we start
        self._loadedObjects = []

        self._api = None

    def _migrateStorageSchema(self, metadata: MetaData) -> None:
        """ Migrate Storage Schema

        Rename the schema

        """

        relDir = self._packageCfg.config.storage.alembicDir(require_string)
        alembicDir = os.path.join(self.rootDir, relDir)
        if not os.path.isdir(alembicDir): raise NotADirectoryError(alembicDir)

        dbConn = DbConnection(
            dbConnectString=self.platform.dbConnectString,
            metadata=metadata,
            alembicDir=alembicDir,
            enableCreateAll=False
        )

        # Rename the plugin schema to core.
        renameToCoreSql = '''
            DO $$
            BEGIN
                IF EXISTS(
                    SELECT schema_name
                      FROM information_schema.schemata
                      WHERE schema_name = 'pl_generic_diagram_menu'
                  )
                THEN
                  EXECUTE ' DROP SCHEMA IF EXISTS pl_diagram_generic_menu CASCADE ';
                  EXECUTE ' ALTER SCHEMA pl_generic_diagram_menu RENAME TO pl_diagram_generic_menu ';
                END IF;
            END
            $$;
        '''

        dbSession = dbConn.ormSessionCreator()
        try:
            dbSession.execute(renameToCoreSql)
            dbSession.commit()

        finally:
            dbSession.close()
            dbConn.dbEngine.dispose()

        PluginServerStorageEntryHookABC._migrateStorageSchema(self, metadata)

    def load(self) -> None:
        """ Load

        This will be called when the plugin is loaded, just after the db is migrated.
        Place any custom initialiastion steps here.

        """
        loadStorageTuples()
        loadPrivateTuples()
        loadPublicTuples()
        logger.debug("Loaded")

    @property
    def dbMetadata(self):
        return DeclarativeBase.metadata

    def start(self):
        """ Start

        This will be called when the plugin is loaded, just after the db is migrated.
        Place any custom initialiastion steps here.

        """

        tupleObservable = makeTupleDataObservableHandler(self.dbSessionCreator)

        self._loadedObjects.extend(
            makeAdminBackendHandlers(tupleObservable, self.dbSessionCreator))

        self._loadedObjects.append(tupleObservable)

        mainController = MainController(
            dbSessionCreator=self.dbSessionCreator,
            tupleObservable=tupleObservable)

        self._loadedObjects.append(mainController)
        self._loadedObjects.append(makeTupleActionProcessorHandler(mainController))

        # Initialise the API object that will be shared with other plugins
        self._api = DiagramGenericMenuApi(mainController)
        self._loadedObjects.append(self._api)

        logger.debug("Started")

    def stop(self):
        """ Stop

        This method is called by the platform to tell the peek app to shutdown and stop
        everything it's doing
        """
        # Shutdown and dereference all objects we constructed when we started
        while self._loadedObjects:
            self._loadedObjects.pop().shutdown()

        self._api = None

        logger.debug("Stopped")

    def unload(self):
        """Unload

        This method is called after stop is called, to unload any last resources
        before the PLUGIN is unlinked from the platform

        """
        logger.debug("Unloaded")

    @property
    def publishedServerApi(self) -> object:
        """ Published Server API
    
        :return  class that implements the API that can be used by other Plugins on this
        platform service.
        """
        return self._api
