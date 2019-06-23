import logging
from typing import Optional

from peek_plugin_base.server.PluginServerEntryHookABC import PluginServerEntryHookABC
from peek_plugin_base.server.PluginServerStorageEntryHookABC import \
    PluginServerStorageEntryHookABC

from peek_core_email._private.server.EmailApi import \
    EmailApi
from peek_core_email._private.server.admin_backend.PeekAdmSettingHandler import \
    createAdminSettingsHandler
from peek_core_email._private.storage.DeclarativeBase import loadStorageTuples

logger = logging.getLogger(__name__)


class PluginServerEntryHook(PluginServerEntryHookABC,
                            PluginServerStorageEntryHookABC):
    def __init__(self, *args, **kwargs):
        PluginServerEntryHookABC.__init__(self, *args, **kwargs)
        self._api = None

        self._handlers = []

    def load(self) -> None:
        loadStorageTuples()

        logger.debug("loaded")

    def start(self):
        # Create the main controller
        self._api = EmailApi(self.dbSessionCreator)
        self._handlers.append(self._api)

        # Add the handlers for the Admin UI
        self._handlers.append(createAdminSettingsHandler(self.dbSessionCreator))

        logger.debug("started")

    def stop(self):
        while self._handlers:
            self._handlers.pop().shutdown()

        logger.debug("stopped")

    def unload(self):
        self._api = None
        logger.debug("unloaded")

    ###### Implement PluginServerStorageEntryHookABC

    @property
    def dbMetadata(self):
        from peek_core_email._private.storage import DeclarativeBase
        return DeclarativeBase.metadata

    ###### Publish our API

    @property
    def publishedServerApi(self) -> Optional[object]:
        return self._api
