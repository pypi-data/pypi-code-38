import ujson as json
import logging
from typing import List

from peek_plugin_diagram._private.worker.tasks.ImportDispTask import importDispsTask
from peek_plugin_livedb.server.LiveDBWriteApiABC import LiveDBWriteApiABC
from twisted.internet.defer import inlineCallbacks
from vortex.SerialiseUtil import convertFromWkbElement

logger = logging.getLogger(__name__)


class DispImportController:
    def __init__(self, liveDbWriteApi: LiveDBWriteApiABC):
        self._liveDbWriteApi = liveDbWriteApi

    def shutdown(self):
        self._liveDbWriteApi = None

    @inlineCallbacks
    def importDisps(self, modelSetKey: str, coordSetKey: str,
                    importGroupHash: str, dispsEncodedPayload: bytes):

        liveDbItemsToImport = yield importDispsTask.delay(
            modelSetKey, coordSetKey, importGroupHash, dispsEncodedPayload
        )

        if liveDbItemsToImport:
            yield self._liveDbWriteApi.importLiveDbItems(
                modelSetKey, liveDbItemsToImport
            )

            yield self._liveDbWriteApi.pollLiveDbValueAcquisition(
                modelSetKey, [i.key for i in liveDbItemsToImport]
            )
