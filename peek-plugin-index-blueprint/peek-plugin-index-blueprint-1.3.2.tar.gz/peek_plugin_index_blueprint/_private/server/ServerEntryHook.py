import logging

from celery import Celery

from peek_plugin_base.server.PluginServerEntryHookABC import PluginServerEntryHookABC
from peek_plugin_base.server.PluginServerStorageEntryHookABC import \
    PluginServerStorageEntryHookABC
from peek_plugin_base.server.PluginServerWorkerEntryHookABC import \
    PluginServerWorkerEntryHookABC
from peek_plugin_index_blueprint._private.server.api.IndexBlueprintApi import IndexBlueprintApi
from peek_plugin_index_blueprint._private.server.client_handlers.ThingIndexChunkLoadRpc import \
    ThingIndexChunkLoadRpc
from peek_plugin_index_blueprint._private.server.client_handlers.ThingIndexChunkUpdateHandler import \
    ThingIndexChunkUpdateHandler
from peek_plugin_index_blueprint._private.server.controller.ThingIndexCompilerController import \
    ThingIndexCompilerController
from peek_plugin_index_blueprint._private.server.controller.ThingIndexImportController import ThingIndexImportController
from peek_plugin_index_blueprint._private.server.controller.ThingIndexStatusController import ThingIndexStatusController
from peek_plugin_index_blueprint._private.storage import DeclarativeBase
from peek_plugin_index_blueprint._private.storage.DeclarativeBase import loadStorageTuples
from peek_plugin_index_blueprint._private.tuples import loadPrivateTuples
from peek_plugin_index_blueprint.tuples import loadPublicTuples
from peek_plugin_index_blueprint.tuples.ThingTuple import ThingTuple
from peek_plugin_index_blueprint.tuples.ThingImportTuple import ThingImportTuple
from vortex.DeferUtil import vortexLogFailure
from vortex.Payload import Payload
from .TupleActionProcessor import makeTupleActionProcessorHandler
from .TupleDataObservable import makeTupleDataObservableHandler
from .admin_backend import makeAdminBackendHandlers
from .controller.MainController import MainController

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

        # ----------------
        # Client Handlers and RPC

        self._loadedObjects += ThingIndexChunkLoadRpc(self.dbSessionCreator).makeHandlers()

        # ----------------
        # ThingIndex client update handler
        thingIndexChunkUpdateHandler = ThingIndexChunkUpdateHandler(
            self.dbSessionCreator
        )
        self._loadedObjects.append(thingIndexChunkUpdateHandler)

        # ----------------
        # ThingIndex Status Controller
        thingIndexStatusController = ThingIndexStatusController()
        self._loadedObjects.append(thingIndexStatusController)

        # ----------------
        # Tuple Observable
        tupleObservable = makeTupleDataObservableHandler(
            dbSessionCreator=self.dbSessionCreator,
            thingIndexStatusController=thingIndexStatusController
        )
        self._loadedObjects.append(tupleObservable)

        # ----------------
        # Admin Handler
        self._loadedObjects.extend(
            makeAdminBackendHandlers(tupleObservable, self.dbSessionCreator)
        )

        # ----------------
        # Tell the status controller about the Tuple Observable
        thingIndexStatusController.setTupleObservable(tupleObservable)

        # ----------------
        # Main Controller
        mainController = MainController(
            dbSessionCreator=self.dbSessionCreator,
            tupleObservable=tupleObservable)

        self._loadedObjects.append(mainController)

        # ----------------
        # Thing Index Compiler Controller
        thingIndexCompilerController = ThingIndexCompilerController(
            dbSessionCreator=self.dbSessionCreator,
            statusController=thingIndexStatusController,
            clientUpdateHandler=thingIndexChunkUpdateHandler
        )
        self._loadedObjects.append(thingIndexCompilerController)

        # ----------------
        # Import Controller
        thingIndexImportController = ThingIndexImportController()
        self._loadedObjects.append(thingIndexImportController)

        # ----------------
        # Setup the Action Processor
        self._loadedObjects.append(makeTupleActionProcessorHandler(mainController))

        # ----------------
        # Setup the APIs
        # Initialise the API object that will be shared with other plugins
        self._api = IndexBlueprintApi(thingIndexImportController)
        self._loadedObjects.append(self._api)

        # ----------------
        # Start the compiler controllers
        thingIndexCompilerController.start()

        self._test()

        logger.debug("Started")

    def _test(self):
        # ----------------
        # API test
        newThings = []
        thing1 = ThingImportTuple(
            key="thing1Key",
            modelSetKey="testModel",
            thingTypeKey="objectType1",
            importGroupHash='test load',
            valueStr="a string",
            valueInt=1
        )

        newThings.append(thing1)
        thing2 = ThingImportTuple(
            key="thing2Key",
            modelSetKey="testModel",
            thingTypeKey="objectType2",
            importGroupHash='test load',
            valueStr="a string",
            valueInt=2
        )

        newThings.append(thing2)

        d = Payload(tuples=newThings).toEncodedPayloadDefer()
        d.addCallback(self._api.createOrUpdateThings)
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
        from peek_plugin_index_blueprint._private.worker.CeleryApp import celeryApp
        return celeryApp
