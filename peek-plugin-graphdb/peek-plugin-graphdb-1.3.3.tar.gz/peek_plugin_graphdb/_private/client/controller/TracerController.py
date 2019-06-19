""" Fast Graph DB

This module stores a memory resident model of a graph network.

"""
import logging

from peek_plugin_graphdb._private.client.controller.FastGraphDb import FastGraphDb
from peek_plugin_graphdb._private.client.controller.ItemKeyIndexCacheController import \
    ItemKeyIndexCacheController
from peek_plugin_graphdb._private.client.controller.PrivateRunTrace import PrivateRunTrace
from peek_plugin_graphdb._private.client.controller.TraceConfigCacheController import \
    TraceConfigCacheController
from peek_plugin_graphdb.tuples.GraphDbTraceResultTuple import GraphDbTraceResultTuple
from vortex.DeferUtil import deferToThreadWrapWithLogger

logger = logging.getLogger(__name__)


class TracerController:
    def __init__(self, fastGraphDb: FastGraphDb,
                 itemKeyCacheController: ItemKeyIndexCacheController,
                 traceConfigCacheController: TraceConfigCacheController):
        self._fastGraphDb = fastGraphDb
        self._itemKeyCacheController = itemKeyCacheController
        self._traceConfigCacheController = traceConfigCacheController

    def shutdown(self):
        self._fastGraphDb = None
        self._itemKeyCacheController = None
        self._traceConfigCacheController = None

    @deferToThreadWrapWithLogger(logger)
    def runTrace(self, modelSetKey, traceConfigKey,
                 startVertexKey) -> GraphDbTraceResultTuple:
        traceConfig = self._traceConfigCacheController.traceConfigTuple(
            modelSetKey=modelSetKey, traceConfigKey=traceConfigKey
        )

        # Prepossess some trace rules
        traceConfig = traceConfig.tupleClone()
        for rule in traceConfig.rules:
            rule.prepare()

        startSegmentKeys = self._itemKeyCacheController.getSegmentKeys(
            modelSetKey=modelSetKey, vertexKey=startVertexKey
        )

        fastGraphDbModel = self._fastGraphDb.graphForModelSet(modelSetKey)

        result = GraphDbTraceResultTuple(
            modelSetKey=modelSetKey,
            traceConfigKey=traceConfigKey,
            startVertexKey=startVertexKey
        )

        PrivateRunTrace(result, traceConfig, fastGraphDbModel,
                        startVertexKey, startSegmentKeys).run()

        return result
