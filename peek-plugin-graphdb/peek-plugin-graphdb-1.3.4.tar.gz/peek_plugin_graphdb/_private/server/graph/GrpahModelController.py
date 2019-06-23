import logging

from twisted.internet.defer import Deferred

from peek_plugin_graphdb._private.server.api.GraphDbReadApi import GraphDbReadApi
from peek_plugin_graphdb._private.storage.GraphDbModelSet import GraphDbModelSet

logger = logging.getLogger(__name__)


class GraphModelController(object):
    def __init__(self, dbSessionCreator,
                 readApi: GraphDbReadApi,
                 modelSet: GraphDbModelSet):

        self._dbSessionCreator = dbSessionCreator
        self._readApi = readApi
        self._modelSet = modelSet


    # ---------------
    # Accessor methods

    def modelSet(self) -> GraphDbModelSet:
        return self._modelSet

    # def edgesForSegmentHash(self, segmentHash: str) -> List[GraphDbImportEdgeTuple]:
    #     return list(self._edgesBySegmentHash.get(segmentHash, []))

    # ---------------
    # Context methods

    def newUpdateContext(self) -> 'GraphUpdateContext':
        from peek_plugin_graphdb._private.server.graph.GraphUpdateContext import \
            GraphUpdateContext
        return GraphUpdateContext(self, self._readApi, self._dbSessionCreator)

    def newSegmentImporter(self) -> 'GraphSegmentImporter':
        from peek_plugin_graphdb._private.server.graph.GraphSegmentImporter import \
            GraphSegmentImporter
        return GraphSegmentImporter(self)

    # ---------------
    # Start/Stop methods

    def start(self) -> Deferred:
        pass

    def shutdown(self):
        pass