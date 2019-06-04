import logging

from peek_plugin_base.client.PluginClientEntryHookABC import PluginClientEntryHookABC

from .DeviceTupleDataObservableProxy import makeDeviceTupleDataObservableProxy

from peek_plugin_branch._private.tuples import loadPrivateTuples
from peek_plugin_branch.tuples import loadPublicTuples

from peek_plugin_branch._private.storage.DeclarativeBase import loadStorageTuples

from .DeviceTupleProcessorActionProxy import makeTupleActionProcessorProxy

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

    def start(self):
        """ Load

        This will be called when the plugin is loaded, just after the db is migrated.
        Place any custom initialiastion steps here.

        """

        self._loadedObjects.append(makeTupleActionProcessorProxy())

        self._loadedObjects.append(makeDeviceTupleDataObservableProxy())

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
