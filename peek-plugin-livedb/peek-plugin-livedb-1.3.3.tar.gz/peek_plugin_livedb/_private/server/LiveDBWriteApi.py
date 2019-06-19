import logging
from datetime import datetime
from typing import List

from sqlalchemy import bindparam
from sqlalchemy.sql.expression import and_
from twisted.internet import defer
from twisted.internet.defer import Deferred, inlineCallbacks

from peek_plugin_livedb._private.server.LiveDBReadApi import LiveDBReadApi
from peek_plugin_livedb._private.server.controller.LiveDbController import \
    LiveDbController
from peek_plugin_livedb._private.server.controller.LiveDbImportController import \
    LiveDbImportController
from peek_plugin_livedb._private.storage.LiveDbItem import LiveDbItem
from peek_plugin_livedb._private.storage.LiveDbModelSet import getOrCreateLiveDbModelSet
from peek_plugin_livedb._private.worker.tasks.LiveDbItemUpdateTask import updateValues
from peek_plugin_livedb.server.LiveDBWriteApiABC import LiveDBWriteApiABC
from peek_plugin_livedb.tuples.ImportLiveDbItemTuple import ImportLiveDbItemTuple
from peek_plugin_livedb.tuples.LiveDbDisplayValueUpdateTuple import \
    LiveDbDisplayValueUpdateTuple
from peek_plugin_livedb.tuples.LiveDbRawValueUpdateTuple import LiveDbRawValueUpdateTuple
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload

logger = logging.getLogger(__name__)


class LiveDBWriteApi(LiveDBWriteApiABC):
    def __init__(self, liveDbController: LiveDbController,
                 liveDbImportController: LiveDbImportController,
                 readApi: LiveDBReadApi,
                 dbSessionCreator,
                 dbEngine):
        self._liveDbController = liveDbController
        self._liveDbImportController = liveDbImportController
        self._readApi = readApi
        self._dbSessionCreator = dbSessionCreator
        self._dbEngine = dbEngine

    def shutdown(self):
        pass

    @inlineCallbacks
    def updateRawValues(self, modelSetName: str,
                        updates: List[LiveDbRawValueUpdateTuple]) -> Deferred:
        """ Update Raw Values

        """
        if not updates:
            return

        yield updateValues.delay(modelSetName, updates, raw=True)
        self._readApi.rawValueUpdatesObservable(modelSetName).on_next(updates)

    @inlineCallbacks
    def updateDisplayValue(self, modelSetName: str,
                           updates: List[LiveDbDisplayValueUpdateTuple]) -> Deferred:
        """ Update Display Values

        """
        if not updates:
            return

        yield updateValues.delay(modelSetName, updates, raw=False)
        self._readApi.displayValueUpdatesObservable(modelSetName).on_next(updates)

    def importLiveDbItems(self, modelSetName: str,
                          newItems: List[ImportLiveDbItemTuple]) -> Deferred:
        if not newItems:
            return defer.succeed(True)

        return self._liveDbImportController.importLiveDbItems(modelSetName, newItems)

    def prioritiseLiveDbValueAcquisition(self, modelSetName: str,
                                         liveDbKeys: List[str]) -> Deferred:
        self._readApi.priorityKeysObservable(modelSetName).on_next(liveDbKeys)
        return defer.succeed(True)

    def pollLiveDbValueAcquisition(self, modelSetName: str,
                                         liveDbKeys: List[str]) -> Deferred:
        self._readApi.pollKeysObservable(modelSetName).on_next(liveDbKeys)
        return defer.succeed(True)

