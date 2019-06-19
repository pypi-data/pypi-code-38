import logging
from typing import Optional

from peek_plugin_base.server.PluginServerEntryHookABC import PluginServerEntryHookABC
from peek_plugin_base.server.PluginServerStorageEntryHookABC import \
    PluginServerStorageEntryHookABC
from peek_plugin_chat._private.server.ChatApi import ChatApi
from peek_plugin_chat._private.server.TupleActionProcessor import \
    makeTupleActionProcessorHandler
from peek_plugin_chat._private.server.TupleDataObservable import \
    makeTupleDataObservableHandler
from peek_plugin_chat._private.server.admin_backend import makeAdminBackendHandlers
from peek_plugin_chat._private.server.controller.MainController import MainController
from peek_plugin_chat._private.server.controller.TaskController import TaskController
from peek_plugin_chat._private.storage import DeclarativeBase, loadStorageTuples
from peek_plugin_chat._private.tuples import loadPrivateTuples
from peek_plugin_chat.tuples import loadPublicTuples
from peek_plugin_inbox.server.InboxApiABC import InboxApiABC
from peek_core_user.server.UserApiABC import UserApiABC

logger = logging.getLogger(__name__)


class ServerEntryHook(PluginServerEntryHookABC, PluginServerStorageEntryHookABC):
    def __init__(self, *args, **kwargs):
        """" Constructor """
        # Call the base classes constructor
        PluginServerEntryHookABC.__init__(self, *args, **kwargs)

        #: Loaded Objects, This is a list of all objects created when we start
        self._loadedObjects = []

        #: The API object for this plugin
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

    def start(self):
        """ Start

        This will be called to start the plugin.
        Start, means what ever we choose to do here. This includes:

        -   Create Controllers

        -   Create payload, observable and tuple action handlers.

        """

        # Create the API
        self._api = ChatApi(self.dbSessionCreator)
        self._loadedObjects.append(self._api)  # For auto shutdown

        userPluginApi = self.platform.getOtherPluginApi("peek_core_user")
        assert isinstance(userPluginApi, UserApiABC), (
            "Expected UserApiABC")

        activeTaskPluginApi = self.platform.getOtherPluginApi("peek_plugin_inbox")
        assert isinstance(activeTaskPluginApi, InboxApiABC), (
            "Expected ActiveTaskApiABC")

        self._loadedObjects.extend(makeAdminBackendHandlers(self.dbSessionCreator))

        # Tuple Observer, required by main controller
        tupleObservable = makeTupleDataObservableHandler(self.dbSessionCreator)
        self._loadedObjects.append(tupleObservable)

        # Controllers
        taskController = TaskController(activeTaskPluginApi)
        self._loadedObjects.append(taskController)

        mainController = MainController(
            ourApi=self._api,
            dbSessionCreator=self.dbSessionCreator,
            tupleObservable=tupleObservable,
            userPluginApi=userPluginApi,
            taskController=taskController).start()
        self._loadedObjects.append(mainController)

        self._api.setMainController(mainController)

        # Tuple Action Processor, requires main controller
        self._loadedObjects.append(makeTupleActionProcessorHandler(mainController))

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
    def dbMetadata(self):
        return DeclarativeBase.metadata


    @property
    def publishedServerApi(self) -> Optional[object]:
        """ Published Server API

        :return  class that implements the API that can be used by other PLUGINs on this
        platform.
        """
        return self._api