import logging
from typing import Optional

from peek_core_email.server.EmailApiABC import EmailApiABC
from peek_plugin_base.server.PluginServerEntryHookABC import PluginServerEntryHookABC
from peek_plugin_base.server.PluginServerStorageEntryHookABC import \
    PluginServerStorageEntryHookABC
from peek_plugin_inbox._private.server.ClientTupleActionProcessor import \
    makeTupleActionProcessorHandler
from peek_plugin_inbox._private.server.ClientTupleDataObservable import \
    makeTupleDataObservableHandler
from peek_plugin_inbox._private.server.InboxApi import InboxApi
from peek_plugin_inbox._private.server.backend.PeekAdmSettingHandler import \
    createAdminSettingsHandler
from peek_plugin_inbox._private.server.controller.MainController import \
    MainController
from peek_plugin_inbox._private.storage.DeclarativeBase import loadStorageTuples
from peek_plugin_inbox._private.tuples import loadPrivateTuples
from peek_plugin_inbox.tuples import loadPublicTuples
from peek_core_user.server.UserApiABC import UserApiABC

logger = logging.getLogger(__name__)


class PluginServerEntryHook(PluginServerEntryHookABC,
                            PluginServerStorageEntryHookABC):
    def __init__(self, *args, **kwargs):
        PluginServerEntryHookABC.__init__(self, *args, **kwargs)
        self._api = None
        self._mainController = None

        self._runningHandlers = []

    def load(self) -> None:
        loadStorageTuples()
        loadPrivateTuples()
        loadPublicTuples()

        logger.debug("loaded")

    def start(self):

        # ----------------
        # Setup the APIs
        userPluginApi = self.platform.getOtherPluginApi("peek_core_user")
        assert isinstance(userPluginApi, UserApiABC), "Expected UserApiABC"

        emailApi = self.platform.getOtherPluginApi("peek_core_email")
        assert isinstance(emailApi, EmailApiABC), "emailApi is not EmailApiABC"

        # ---------------
        # Tuple Observable
        tupleObserver = makeTupleDataObservableHandler(self.dbSessionCreator)
        self._runningHandlers.append(tupleObserver)

        # ---------------
        # MainController
        self._mainController = MainController(
            ormSessionCreator=self.dbSessionCreator,
            userPluginApi=userPluginApi,
            emailApi=emailApi,
            tupleObserver=tupleObserver
        )
        self._runningHandlers.append(self._mainController)

        # ---------------
        # Tuple Action Processor
        actionProcessor = makeTupleActionProcessorHandler(self._mainController)
        self._runningHandlers.append(actionProcessor)

        # ---------------
        # Our API
        # Create the API that other plugins will use
        self._api = InboxApi(
            self.dbSessionCreator, userPluginApi, self._mainController
        )
        self._runningHandlers.append(self._api)


        # ---------------
        # Link API to Main Controller
        self._mainController.setOurApi(self._api)

        # ---------------
        # Admin Handlers
        # Add the handlers for the Admin UI
        self._runningHandlers.append(createAdminSettingsHandler(self.dbSessionCreator))

        self._mainController.start()

        logger.debug("started")

    def stop(self):
        while self._runningHandlers:
            self._runningHandlers.pop().shutdown()

        logger.debug("stopped")

    def unload(self):
        self._mainController = None
        self._api = None
        logger.debug("unloaded")

    ###### Implement PluginServerStorageEntryHookABC

    @property
    def dbMetadata(self):
        from peek_plugin_inbox._private.storage import DeclarativeBase
        return DeclarativeBase.metadata

    ###### Publish our API

    @property
    def publishedServerApi(self) -> Optional[object]:
        return self._api
