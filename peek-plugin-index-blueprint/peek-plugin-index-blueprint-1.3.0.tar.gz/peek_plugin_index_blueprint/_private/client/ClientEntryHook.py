import logging

from twisted.internet.defer import inlineCallbacks

from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_base.client.PluginClientEntryHookABC import PluginClientEntryHookABC
from peek_plugin_index_blueprint._private.PluginNames import indexBlueprintFilt, \
    indexBlueprintActionProcessorName
from peek_plugin_index_blueprint._private.PluginNames import indexBlueprintObservableName
from peek_plugin_index_blueprint._private.client.ClientTupleObservable import \
    makeClientTupleDataObservableHandler
from peek_plugin_index_blueprint._private.client.controller.ThingIndexCacheController import \
    ThingIndexCacheController
from peek_plugin_index_blueprint._private.client.handlers.ThingIndexCacheHandler import \
    ThingIndexCacheHandler
from peek_plugin_index_blueprint._private.storage.DeclarativeBase import loadStorageTuples
from peek_plugin_index_blueprint._private.tuples import loadPrivateTuples
from peek_plugin_index_blueprint.tuples import loadPublicTuples
from vortex.handler.TupleActionProcessorProxy import TupleActionProcessorProxy
from vortex.handler.TupleDataObservableProxyHandler import TupleDataObservableProxyHandler
from vortex.handler.TupleDataObserverClient import TupleDataObserverClient

logger = logging.getLogger(__name__)


class ClientEntryHook(PluginClientEntryHookABC):
    def __init__(self, *args, **kwargs):
        """" Constructor """
        # Call the base classes constructor
        PluginClientEntryHookABC.__init__(self, *args, **kwargs)

        #: Loaded Objects, This is a list of all objects created when we start
        self._loadedObjects = []

    def load(self) -> None:
        """ Load

        This will be called when the plugin is loaded, just after the db is migrated.
        Place any custom initialiastion steps here.

        """

        loadStorageTuples()

        loadPrivateTuples()
        loadPublicTuples()

        logger.debug("Loaded")

    @inlineCallbacks
    def start(self):
        """ Load

        This will be called when the plugin is loaded, just after the db is migrated.
        Place any custom initialisation steps here.

        """

        # ----------------
        # Proxy actions back to the server, we don't process them at all
        self._loadedObjects.append(
            TupleActionProcessorProxy(
                tupleActionProcessorName=indexBlueprintActionProcessorName,
                proxyToVortexName=peekServerName,
                additionalFilt=indexBlueprintFilt)
        )

        # ----------------
        # Provide the devices access to the servers observable
        tupleDataObservableProxyHandler = TupleDataObservableProxyHandler(
            observableName=indexBlueprintObservableName,
            proxyToVortexName=peekServerName,
            additionalFilt=indexBlueprintFilt,
            observerName="Proxy to devices")
        self._loadedObjects.append(tupleDataObservableProxyHandler)

        # ----------------
        #: This is an observer for us (the client) to use to observe data
        # from the server
        serverTupleObserver = TupleDataObserverClient(
            observableName=indexBlueprintObservableName,
            destVortexName=peekServerName,
            additionalFilt=indexBlueprintFilt,
            observerName="Data for client"
        )
        self._loadedObjects.append(serverTupleObserver)

        # ----------------
        # ThingIndex Cache Controller

        thingIndexCacheController = ThingIndexCacheController(
            self.platform.serviceId
        )
        self._loadedObjects.append(thingIndexCacheController)

        # ----------------
        # ThingIndex Cache Handler

        thingIndexHandler = ThingIndexCacheHandler(
            cacheController=thingIndexCacheController,
            clientId=self.platform.serviceId
        )
        self._loadedObjects.append(thingIndexHandler)

        # ----------------
        # Set the caches reference to the handler
        thingIndexCacheController.setThingIndexCacheHandler(thingIndexHandler)

        # ----------------
        # Create the Tuple Observer
        makeClientTupleDataObservableHandler(tupleDataObservableProxyHandler,
                                             thingIndexCacheController)

        # ----------------
        # Start the compiler controllers
        yield thingIndexCacheController.start()

        logger.debug("Started")

    def stop(self):
        """ Stop

        This method is called by the platform to tell the peek app to shutdown and stop
        everything it's doing
        """
        # Shutdown and dereference all objects we constructed when we started
        while self._loadedObjects:
            self._loadedObjects.pop().shutdown()

        logger.debug("Stopped")

    def unload(self):
        """Unload

        This method is called after stop is called, to unload any last resources
        before the PLUGIN is unlinked from the platform

        """
        logger.debug("Unloaded")
