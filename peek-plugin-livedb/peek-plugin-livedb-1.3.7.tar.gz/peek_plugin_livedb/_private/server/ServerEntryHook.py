import logging

from celery import Celery

from peek_plugin_base.server.PluginServerEntryHookABC import PluginServerEntryHookABC
from peek_plugin_base.server.PluginServerStorageEntryHookABC import \
    PluginServerStorageEntryHookABC
from peek_plugin_base.server.PluginServerWorkerEntryHookABC import \
    PluginServerWorkerEntryHookABC
from peek_plugin_livedb._private.server.controller.LiveDbController import \
    LiveDbController
from peek_plugin_livedb._private.server.controller.LiveDbImportController import \
    LiveDbImportController
from peek_plugin_livedb._private.storage import DeclarativeBase
from peek_plugin_livedb._private.storage.DeclarativeBase import loadStorageTuples
from peek_plugin_livedb._private.tuples import loadPrivateTuples
from peek_plugin_livedb.tuples import loadPublicTuples
from .LiveDBApi import LiveDBApi
from .TupleActionProcessor import makeTupleActionProcessorHandler
from .TupleDataObservable import makeTupleDataObservableHandler
from .admin_backend import makeAdminBackendHandlers
from .controller.MainController import MainController

logger = logging.getLogger(__name__)


class ServerEntryHook(PluginServerEntryHookABC, PluginServerStorageEntryHookABC,
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

        tupleObservable = makeTupleDataObservableHandler(self.dbSessionCreator)

        self._loadedObjects.extend(
            makeAdminBackendHandlers(tupleObservable, self.dbSessionCreator))

        self._loadedObjects.append(tupleObservable)

        # session = self.dbSessionCreator()
        #
        # This will retrieve all the settings
        # from peek_plugin_livedb._private.storage.Setting import globalSetting
        # allSettings = globalSetting(session)
        # logger.debug(allSettings)
        #
        # This will retrieve the value of property1
        # from peek_plugin_livedb._private.storage.Setting import PROPERTY1
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

        liveDbController = LiveDbController(self.dbSessionCreator)
        self._loadedObjects.append(liveDbController)

        liveDbImportController = LiveDbImportController(self.dbSessionCreator)
        self._loadedObjects.append(liveDbImportController)

        # Initialise the API object that will be shared with other plugins
        self._api = LiveDBApi(liveDbController=liveDbController,
                              liveDbImportController=liveDbImportController,
                              dbSessionCreator=self.dbSessionCreator,
                              dbEngine=self.dbEngine)
        self._loadedObjects.append(self._api)

        # noinspection PyTypeChecker
        liveDbImportController.setReadApi(self._api.readApi)

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

    ###### Implement PluginServerWorkerEntryHookABC

    @property
    def celeryApp(self) -> Celery:
        from peek_plugin_livedb._private.worker.CeleryApp import celeryApp
        return celeryApp
