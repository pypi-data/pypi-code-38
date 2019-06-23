import logging
from os import path as osp

from twisted.internet.defer import inlineCallbacks

from peek_plugin_base.PeekVortexUtil import peekServerName
from peek_plugin_base.client.PluginClientEntryHookABC import PluginClientEntryHookABC
from peek_plugin_diagram._private.PluginNames import diagramActionProcessorName
from peek_plugin_diagram._private.PluginNames import diagramFilt
from peek_plugin_diagram._private.PluginNames import diagramObservableName
from peek_plugin_diagram._private.client.TupleDataObservable import \
    makeClientTupleDataObservableHandler
from peek_plugin_diagram._private.client.controller.BranchIndexCacheController import \
    BranchIndexCacheController
from peek_plugin_diagram._private.client.controller.CoordSetCacheController import \
    CoordSetCacheController
from peek_plugin_diagram._private.client.controller.GridCacheController import \
    GridCacheController
from peek_plugin_diagram._private.client.controller.LocationIndexCacheController import \
    LocationIndexCacheController
from peek_plugin_diagram._private.client.controller.LookupCacheController import \
    LookupCacheController
from peek_plugin_diagram._private.client.controller.ModelSetCacheController import \
    ModelSetCacheController
from peek_plugin_diagram._private.client.handlers.BranchIndexCacheHandler import \
    BranchIndexCacheHandler
from peek_plugin_diagram._private.client.handlers.GridCacheHandler import GridCacheHandler
from peek_plugin_diagram._private.client.handlers.LocationIndexCacheHandler import \
    LocationIndexCacheHandler
from peek_plugin_diagram._private.storage.DeclarativeBase import loadStorageTuples
from peek_plugin_diagram._private.tuples import loadPrivateTuples
from peek_plugin_diagram.tuples import loadPublicTuples
from txhttputil.site.FileUnderlayResource import FileUnderlayResource
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
        Place any custom initialiastion steps here.

        """

        # Proxy actions back to the server, we don't process them at all
        self._loadedObjects.append(
            TupleActionProcessorProxy(
                tupleActionProcessorName=diagramActionProcessorName,
                proxyToVortexName=peekServerName,
                additionalFilt=diagramFilt)
        )

        # Provide the devices access to the servers observable
        tupleDataObservableProxyHandler = TupleDataObservableProxyHandler(
            observableName=diagramObservableName,
            proxyToVortexName=peekServerName,
            additionalFilt=diagramFilt,
            observerName="Proxy to devices")
        self._loadedObjects.append(tupleDataObservableProxyHandler)

        #: This is an observer for us (the client) to use to observe data
        # from the server
        serverTupleObserver = TupleDataObserverClient(
            observableName=diagramObservableName,
            destVortexName=peekServerName,
            additionalFilt=diagramFilt,
            observerName="Data for us"
        )
        self._loadedObjects.append(serverTupleObserver)

        # -----

        # Buffer the lookups in the client (us)
        lookupCacheController = LookupCacheController(serverTupleObserver)
        self._loadedObjects.append(lookupCacheController)

        # Buffer the model sets in the client (us)
        modelSetCacheController = ModelSetCacheController(serverTupleObserver)
        self._loadedObjects.append(modelSetCacheController)

        # Buffer the coord sets in the client (us)
        coordSetCacheController = CoordSetCacheController(serverTupleObserver)
        self._loadedObjects.append(coordSetCacheController)

        # ----- Grid Cache Controller
        gridCacheController = GridCacheController(self.platform.serviceId)
        self._loadedObjects.append(gridCacheController)

        # This is the custom handler for the client
        gridCacheHandler = GridCacheHandler(
            gridCacheController=gridCacheController,
            clientId=self.platform.serviceId
        )
        self._loadedObjects.append(gridCacheHandler)

        gridCacheController.setGridCacheHandler(gridCacheHandler)

        # ----- Location Index Cache Controller

        locationIndexCacheController = LocationIndexCacheController(
            self.platform.serviceId)
        self._loadedObjects.append(locationIndexCacheController)

        # This is the custom handler for the client
        locationIndexCacheHandler = LocationIndexCacheHandler(
            locationIndexCacheController=locationIndexCacheController,
            clientId=self.platform.serviceId
        )
        self._loadedObjects.append(locationIndexCacheHandler)

        locationIndexCacheController.setLocationIndexCacheHandler(
            locationIndexCacheHandler)

        # ----------------
        # BranchIndex Cache Controller

        branchIndexCacheController = BranchIndexCacheController(
            self.platform.serviceId
        )
        self._loadedObjects.append(branchIndexCacheController)

        # ----------------
        # BranchIndex Cache Handler

        branchIndexHandler = BranchIndexCacheHandler(
            cacheController=branchIndexCacheController,
            clientId=self.platform.serviceId
        )
        self._loadedObjects.append(branchIndexHandler)
        branchIndexCacheController.setBranchIndexCacheHandler(branchIndexHandler)

        # -----
        # Create the Tuple Observer
        tupleObservable = makeClientTupleDataObservableHandler(
            tupleDataObservableProxyHandler,
            modelSetCacheController,
            coordSetCacheController,
            gridCacheController,
            lookupCacheController,
            locationIndexCacheController,
            branchIndexCacheController
        )
        # This is already in the _loadedObjects, it's tupleDataObservableProxyHandler

        # ----------------
        # Set the caches reference to the handler
        lookupCacheController.setTupleObservable(tupleObservable)
        modelSetCacheController.setTupleObservable(tupleObservable)
        coordSetCacheController.setTupleObservable(tupleObservable)

        yield locationIndexCacheController.start()
        yield branchIndexCacheController.start()
        yield gridCacheController.start()
        lookupCacheController.start()
        modelSetCacheController.start()
        coordSetCacheController.start()

        # THIS WILL BE USED WHEN THE DEVICE IS RUNNING NS LIVE SYNC
        # Add in the HTTP resource that allows images to be downloaded
        resource = FileUnderlayResource()
        distDir = osp.join(osp.dirname(osp.dirname(__file__)), "ns-assets", "www")
        resource.addFileSystemRoot(distDir)
        resource.enableSinglePageApplication()

        self.platform.addMobileResource(b'web_dist', resource)

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
