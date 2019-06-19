import logging
from typing import List

from twisted.internet.defer import inlineCallbacks, Deferred

from peek_plugin_graphdb._private.server.client_handlers.TraceConfigUpdateHandler import \
    TraceConfigUpdateHandler
from peek_plugin_graphdb._private.worker.tasks import SegmentIndexImporter
from peek_plugin_graphdb._private.worker.tasks import TraceConfigImporter

logger = logging.getLogger(__name__)


class ImportController:
    def __init__(self, traceConfigUpdateHandler: TraceConfigUpdateHandler):
        self._traceConfigUpdateHandler = traceConfigUpdateHandler

    def shutdown(self):
        pass

    @inlineCallbacks
    def createOrUpdateSegments(self, graphSegmentEncodedPayload: bytes):
        yield SegmentIndexImporter.createOrUpdateSegments.delay(
            graphSegmentEncodedPayload
        )

    @inlineCallbacks
    def deleteSegment(self, modelSetKey: str, importGroupHashes: List[str]):
        yield SegmentIndexImporter.deleteSegment.delay(modelSetKey, importGroupHashes)

    @inlineCallbacks
    def createOrUpdateTraceConfig(self, traceEncodedPayload: bytes) -> Deferred:
        insertedOrCreated = yield TraceConfigImporter.createOrUpdateTraceConfigs.delay(
            traceEncodedPayload
        )

        for modelSetKey, traceConfigKeys in insertedOrCreated.items():
            self._traceConfigUpdateHandler.sendCreatedOrUpdatedUpdates(
                modelSetKey, traceConfigKeys
            )

    @inlineCallbacks
    def deleteTraceConfig(self, modelSetKey: str, traceConfigKeys: List[str]) -> Deferred:
        yield TraceConfigImporter.deleteTraceConfig.delay(
            modelSetKey, traceConfigKeys
        )

        self._traceConfigUpdateHandler.sendDeleted(
            modelSetKey, traceConfigKeys
        )
