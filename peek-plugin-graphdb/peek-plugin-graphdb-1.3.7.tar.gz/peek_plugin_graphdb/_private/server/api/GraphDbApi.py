from typing import List

from twisted.internet import defer
from twisted.internet.defer import Deferred

from peek_plugin_graphdb._private.server.controller.ImportController import \
    ImportController
from peek_plugin_graphdb.server.GraphDbApiABC import GraphDbApiABC
from peek_plugin_graphdb.tuples.GraphDbImportSegmentTuple import GraphDbImportSegmentTuple


class GraphDbApi(GraphDbApiABC):
    def __init__(self, importController: ImportController):
        self._importController = importController

    def shutdown(self):
        self._importController = None

    def createOrUpdateSegment(self, graphSegmentEncodedPayload: bytes) -> Deferred:
        
        return self._importController.createOrUpdateSegments(
             graphSegmentEncodedPayload
        )

    def deleteSegments(self, modelSetKey: str, importGroupHashes: List[str]) -> Deferred:
        return self._importController.deleteSegment(modelSetKey, importGroupHashes)

    def createOrUpdateTraceConfig(self, traceEncodedPayload: bytes) -> Deferred:
        return self._importController.createOrUpdateTraceConfig(
            traceEncodedPayload
        )

    def deleteTraceConfig(self, modelSetKey:str, traceConfigKeys: List[str]) -> Deferred:
        return self._importController.deleteTraceConfig(modelSetKey, traceConfigKeys)
