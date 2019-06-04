import logging

from peek_plugin_inbox.server.InboxApiABC import InboxApiABC
from peek_plugin_base.server.PluginServerEntryHookABC import PluginServerEntryHookABC

from peek_plugin_tutorial._private.storage import DeclarativeBase
from peek_plugin_tutorial._private.storage.DeclarativeBase import loadStorageTuples

from peek_plugin_base.server.PluginServerStorageEntryHookABC import \
    PluginServerStorageEntryHookABC

from peek_plugin_tutorial._private.tuples import loadPrivateTuples
from peek_plugin_tutorial.tuples import loadPublicTuples

from .TupleDataObservable import makeTupleDataObservableHandler

from .TupleActionProcessor import makeTupleActionProcessorHandler
from .controller.MainController import MainController

from .admin_backend import makeAdminBackendHandlers

from .agent_handlers.RpcForAgent import RpcForAgent

from .ServerToAgentRpcCallExample import ServerToAgentRpcCallExample

from .TutorialApi import TutorialApi

from .ExampleUseTaskApi import ExampleUseTaskApi

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

        tupleObservable = makeTupleDataObservableHandler(self.dbSessionCreator)

        self._loadedObjects.extend(
            makeAdminBackendHandlers(tupleObservable, self.dbSessionCreator))

        self._loadedObjects.append(tupleObservable)

        # session = self.dbSessionCreator()
        #
        # This will retrieve all the settings
        # from peek_plugin_tutorial._private.storage.Setting import globalSetting
        # allSettings = globalSetting(session)
        # logger.debug(allSettings)
        #
        # This will retrieve the value of property1
        # from peek_plugin_tutorial._private.storage.Setting import PROPERTY1
        # value1 = globalSetting(session, key=PROPERTY1)
        # logger.debug("value1 = %s" % value1)
        #
        # This will set property1
        # globalSetting(session, key=PROPERTY1, value="new value 1")
        # session.commit()
        #
        # session.close()

        mainController = MainController(
            dbSessionCreator=self.dbSessionCreator,
            tupleObservable=tupleObservable)

        self._loadedObjects.append(mainController)
        self._loadedObjects.append(makeTupleActionProcessorHandler(mainController))

        # Initialise the RpcForAgent
        self._loadedObjects.extend(RpcForAgent(mainController, self.dbSessionCreator)
                                   .makeHandlers())

        # Initialise and start the RPC for Server
        self._loadedObjects.append(ServerToAgentRpcCallExample().start())

        # Initialise the API object that will be shared with other plugins
        self._api = TutorialApi(mainController)
        self._loadedObjects.append(self._api)

        # Get a reference for the Active Task
        activeTaskApi = self.platform.getOtherPluginApi("peek_plugin_inbox")
        assert isinstance(activeTaskApi, InboxApiABC), "Wrong activeTaskApi"

        # Initialise the example code that will send the test task
        self._loadedObjects.append(
            ExampleUseTaskApi(mainController, activeTaskApi).start()
        )

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
