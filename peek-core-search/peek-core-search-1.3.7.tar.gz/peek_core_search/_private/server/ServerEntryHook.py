import logging
import os

from celery import Celery
from jsoncfg.value_mappers import require_string
from sqlalchemy import MetaData

from peek_plugin_base.server.PluginServerEntryHookABC import PluginServerEntryHookABC
from peek_plugin_base.server.PluginServerStorageEntryHookABC import \
    PluginServerStorageEntryHookABC
from peek_plugin_base.server.PluginServerWorkerEntryHookABC import \
    PluginServerWorkerEntryHookABC
from peek_core_search._private.storage import DeclarativeBase
from peek_core_search._private.storage.DeclarativeBase import loadStorageTuples
from peek_core_search._private.storage.Setting import globalSetting, \
    KEYWORD_COMPILER_ENABLED, OBJECT_COMPILER_ENABLED, globalProperties
from peek_core_search._private.tuples import loadPrivateTuples
from peek_core_search.tuples import loadPublicTuples
from peek_core_search.tuples.ImportSearchObjectRouteTuple import \
    ImportSearchObjectRouteTuple
from peek_core_search.tuples.ImportSearchObjectTuple import ImportSearchObjectTuple
from twisted.internet.defer import inlineCallbacks
from vortex.DeferUtil import vortexLogFailure, deferToThreadWrapWithLogger
from vortex.Payload import Payload

from peek_plugin_base.storage.DbConnection import DbConnection
from .TupleActionProcessor import makeTupleActionProcessorHandler
from .TupleDataObservable import makeTupleDataObservableHandler
from .admin_backend import makeAdminBackendHandlers
from .api.SearchApi import SearchApi
from .client_handlers.ClientChunkLoadRpc import ClientChunkLoadRpc
from .client_handlers.ClientSearchIndexChunkUpdateHandler import \
    ClientSearchIndexChunkUpdateHandler
from .client_handlers.ClientSearchObjectChunkUpdateHandler import \
    ClientSearchObjectChunkUpdateHandler
from .controller.MainController import MainController
from .controller.SearchIndexChunkCompilerQueueController import \
    SearchIndexChunkCompilerQueueController
from .controller.SearchObjectChunkCompilerQueueController import \
    SearchObjectChunkCompilerQueueController
from .controller.SearchObjectImportController import SearchObjectImportController
from .controller.StatusController import StatusController

logger = logging.getLogger(__name__)


class ServerEntryHook(PluginServerEntryHookABC,
                      PluginServerStorageEntryHookABC,
                      PluginServerWorkerEntryHookABC):
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
                      WHERE schema_name = 'pl_search'
                  )
                THEN
                  EXECUTE ' DROP SCHEMA IF EXISTS  core_search CASCADE ';
                  EXECUTE ' ALTER SCHEMA pl_search RENAME TO core_search ';
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

    @inlineCallbacks
    def start(self):
        """ Start

        This will be called when the plugin is loaded, just after the db is migrated.
        Place any custom initialiastion steps here.

        """

        # ----------------
        # Client Handlers and RPC

        self._loadedObjects += ClientChunkLoadRpc(self.dbSessionCreator).makeHandlers()

        # ----------------
        # Client Search Index client update handler
        clientSearchIndexChunkUpdateHandler = ClientSearchIndexChunkUpdateHandler(
            self.dbSessionCreator
        )
        self._loadedObjects.append(clientSearchIndexChunkUpdateHandler)

        # ----------------
        # Client Search Object client update handler
        clientSearchObjectChunkUpdateHandler = ClientSearchObjectChunkUpdateHandler(
            self.dbSessionCreator
        )
        self._loadedObjects.append(clientSearchObjectChunkUpdateHandler)

        # ----------------
        # Status Controller
        statusController = StatusController()
        self._loadedObjects.append(statusController)

        # ----------------
        # Tuple Observable
        tupleObservable = makeTupleDataObservableHandler(
            dbSessionCreator=self.dbSessionCreator,
            statusController=statusController
        )
        self._loadedObjects.append(tupleObservable)

        # ----------------
        # Admin Handler
        self._loadedObjects.extend(
            makeAdminBackendHandlers(tupleObservable, self.dbSessionCreator)
        )

        # ----------------
        # Tell the status controller about the Tuple Observable
        statusController.setTupleObservable(tupleObservable)

        # ----------------
        # Main Controller
        mainController = MainController(
            dbSessionCreator=self.dbSessionCreator,
            tupleObservable=tupleObservable)

        self._loadedObjects.append(mainController)

        # ----------------
        # Search Index Controller
        searchIndexChunkCompilerQueueController = SearchIndexChunkCompilerQueueController(
            dbSessionCreator=self.dbSessionCreator,
            statusController=statusController,
            clientSearchIndexUpdateHandler=clientSearchIndexChunkUpdateHandler
        )
        self._loadedObjects.append(searchIndexChunkCompilerQueueController)

        # ----------------
        # Search Object Controller
        searchObjectChunkCompilerQueueController = SearchObjectChunkCompilerQueueController(
            dbSessionCreator=self.dbSessionCreator,
            statusController=statusController,
            clientSearchObjectUpdateHandler=clientSearchObjectChunkUpdateHandler
        )
        self._loadedObjects.append(searchObjectChunkCompilerQueueController)

        # ----------------
        # Import Controller
        searchObjectImportController = SearchObjectImportController()
        self._loadedObjects.append(searchObjectImportController)

        # ----------------
        # Setup the Action Processor
        self._loadedObjects.append(makeTupleActionProcessorHandler(mainController))

        # ----------------
        # Setup the APIs
        # Initialise the API object that will be shared with other plugins
        self._api = SearchApi(searchObjectImportController)
        self._loadedObjects.append(self._api)

        # ----------------
        # Start the compiler controllers

        settings = yield self._loadSettings()

        if settings[KEYWORD_COMPILER_ENABLED]:
            searchIndexChunkCompilerQueueController.start()

        if settings[OBJECT_COMPILER_ENABLED]:
            searchObjectChunkCompilerQueueController.start()

        # self._test()

        logger.debug("Started")

    def _test(self):
        # ----------------
        # API test
        searchObjects = []
        so1 = ImportSearchObjectTuple(
            key="so1key",
            properties={
                "name": "134 Ocean Parade, Circuit breaker 1",
                "alias": "SO1ALIAS"
            }
        )

        so1.routes.append(ImportSearchObjectRouteTuple(
            importGroupHash="importHash1",
            routeTitle="SO1 Route1",
            routePath="/route/for/so1"
        ))

        so1.routes.append(ImportSearchObjectRouteTuple(
            importGroupHash="importHash2",
            routeTitle="SO1 Route2",
            routePath="/route/for/so2"
        ))

        searchObjects.append(so1)
        so2 = ImportSearchObjectTuple(
            key="so2key",
            properties={
                "name": "69 Sheep Farmers Rd Sub TX breaker",
                "alias": "SO2ALIAS"
            }
        )

        so2.routes.append(ImportSearchObjectRouteTuple(
            importGroupHash="importHash1",
            routeTitle="SO2 Route1",
            routePath="/route/for/so2/r2"
        ))

        so2.routes.append(ImportSearchObjectRouteTuple(
            importGroupHash="importHash2",
            routeTitle="SO2 Route2",
            routePath="/route/for/so2/r2"
        ))

        searchObjects.append(so2)

        d = Payload(tuples=searchObjects).toEncodedPayloadDefer()
        d.addCallback(self._api.importSearchObjects)
        d.addErrback(vortexLogFailure, logger, consumeError=True)

        searchObjects = []
        # Try an update of the object, it should add to the props
        so1v2 = ImportSearchObjectTuple(key="so1key", properties={"additional": "ADMS"})
        searchObjects.append(so1v2)

        # This should do nothing
        so2v2 = ImportSearchObjectTuple(
            key="so2key",
            properties=None,
            objectType='Equipment'
        )
        searchObjects.append(so2v2)
        searchObjects.append(so1v2)

        # This should do nothing
        so3v2 = ImportSearchObjectTuple(
            key="so3key",
            properties=None,
            objectType='Job'
        )
        searchObjects.append(so3v2)

        d = Payload(tuples=searchObjects).toEncodedPayloadDefer()
        d.addCallback(self._api.importSearchObjects)
        d.addErrback(vortexLogFailure, logger, consumeError=True)

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

    ###### Implement PluginServerWorkerEntryHookABC

    @property
    def celeryApp(self) -> Celery:
        from peek_core_search._private.worker.CeleryApp import celeryApp
        return celeryApp

    @deferToThreadWrapWithLogger(logger)
    def _loadSettings(self):
        dbSession = self.dbSessionCreator()
        try:
            return {globalProperties[p.key]: p.value
                    for p in globalSetting(dbSession).propertyObjects}

        finally:
            dbSession.close()
