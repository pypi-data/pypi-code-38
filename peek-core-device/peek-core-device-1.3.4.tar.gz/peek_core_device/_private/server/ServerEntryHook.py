import logging

from peek_core_device._private.server.controller.NotifierController import \
    NotifierController
from txhttputil.site.FileUnderlayResource import FileUnderlayResource

from peek_core_device._private.server.controller.UpdateController import \
    UpdateController
from peek_core_device._private.server.controller.EnrollmentController import \
    EnrollmentController
from peek_core_device._private.server.controller.OnlineController import OnlineController
from peek_core_device._private.server.update_resources.DeviceUpdateUploadResource import \
    DeviceUpdateUploadResource
from peek_core_device._private.storage import DeclarativeBase
from peek_core_device._private.storage.DeclarativeBase import loadStorageTuples
from peek_core_device._private.tuples import loadPrivateTuples
from peek_core_device.tuples import loadPublicTuples
from peek_plugin_base.server.PluginServerEntryHookABC import PluginServerEntryHookABC
from peek_plugin_base.server.PluginServerStorageEntryHookABC import \
    PluginServerStorageEntryHookABC
from .DeviceApi import DeviceApi
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
        self._deviceUpdatesPath = None

    @property
    def dbMetadata(self):
        return DeclarativeBase.metadata

    def load(self) -> None:
        """ Load

        This will be called when the plugin is loaded, just after the db is migrated.
        Place any custom initialiastion steps here.

        """
        self._deviceUpdatesPath = self.platform.fileStorageDirectory / "device_update"
        self._deviceUpdatesPath.mkdir(parents=True, exist_ok=True)
        
        loadStorageTuples()
        loadPrivateTuples()
        loadPublicTuples()
        logger.debug("Loaded")

    def start(self):
        """ Start

        This will be called when the plugin is loaded, just after the db is migrated.
        Place any custom initialiastion steps here.

        """

        tupleObservable = makeTupleDataObservableHandler(self.dbSessionCreator)
        self._loadedObjects.append(tupleObservable)

        notifierController = NotifierController(tupleObservable=tupleObservable)
        self._loadedObjects.append(notifierController)

        mainController = MainController(
            dbSessionCreator=self.dbSessionCreator,
            notifierController=notifierController,
            deviceUpdateFilePath=self._deviceUpdatesPath)
        self._loadedObjects.append(mainController)

        # Support uploads from the admin UI
        # noinspection PyTypeChecker
        self.platform.addAdminResource(
            b'create_device_update',
            DeviceUpdateUploadResource(mainController.deviceUpdateController)
        )
        
        # Add the resource that the client uses to download the updates from the server
        updateDownloadResource = FileUnderlayResource()
        updateDownloadResource.addFileSystemRoot(str(self._deviceUpdatesPath))
        # noinspection PyTypeChecker
        self.platform.addServerResource(b'device_update', updateDownloadResource)

        self._loadedObjects.extend(
            makeAdminBackendHandlers(tupleObservable, self.dbSessionCreator)
        )

        # Make the Action Processor Handler
        self._loadedObjects.append(makeTupleActionProcessorHandler(mainController))

        # Initialise the API object that will be shared with other plugins
        self._api = DeviceApi(mainController, self.dbSessionCreator)
        self._loadedObjects.append(self._api)

        notifierController.setApi(self._api)

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
