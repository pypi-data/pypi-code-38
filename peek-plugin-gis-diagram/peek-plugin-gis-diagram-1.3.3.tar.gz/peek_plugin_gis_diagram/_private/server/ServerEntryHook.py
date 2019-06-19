import logging

from peek_plugin_gis_diagram._private.storage import DeclarativeBase
from peek_plugin_gis_diagram._private.storage.DeclarativeBase import loadStorageTuples
from peek_plugin_gis_diagram._private.tuples import loadPrivateTuples
from peek_plugin_gis_diagram.tuples import loadPublicTuples

from peek_plugin_base.server.PluginServerEntryHookABC import PluginServerEntryHookABC
from peek_plugin_base.server.PluginServerStorageEntryHookABC import \
    PluginServerStorageEntryHookABC
from peek_plugin_diagram.server.DiagramViewerApiABC import DiagramViewerApiABC

from peek_plugin_diagram.server.DiagramApiABC import DiagramApiABC
from .GisDiagramApi import GisDiagramApi
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

        diagramPluginApi: DiagramApiABC = self.platform.getOtherPluginApi(
            "peek_plugin_diagram"
        )
        diagramPluginViewerApi: DiagramViewerApiABC = diagramPluginApi.viewerApi()

        tupleObservable = makeTupleDataObservableHandler(diagramPluginViewerApi,
                                                         self.dbSessionCreator)

        self._loadedObjects.extend(
            makeAdminBackendHandlers(tupleObservable, self.dbSessionCreator)
        )

        self._loadedObjects.append(tupleObservable)

        mainController = MainController(
            dbSessionCreator=self.dbSessionCreator,
            tupleObservable=tupleObservable)

        self._loadedObjects.append(mainController)
        self._loadedObjects.append(makeTupleActionProcessorHandler(mainController))

        # Initialise the API object that will be shared with other plugins
        self._api = GisDiagramApi(mainController)
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
