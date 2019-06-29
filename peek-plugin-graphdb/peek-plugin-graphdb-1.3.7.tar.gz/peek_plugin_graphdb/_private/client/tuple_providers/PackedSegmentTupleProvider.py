import json
import logging
from collections import defaultdict
from typing import Union, List

from peek_plugin_graphdb._private.tuples.GraphDbPackedSegmentTuple import \
    GraphDbPackedSegmentTuple
from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_plugin_graphdb._private.client.controller.SegmentCacheController import \
    SegmentCacheController
from peek_plugin_graphdb._private.tuples.GraphDbEncodedChunkTuple import \
    GraphDbEncodedChunkTuple
from peek_plugin_graphdb._private.worker.tasks._SegmentIndexCalcChunkKey import \
    makeChunkKeyForSegmentKey

logger = logging.getLogger(__name__)


class PackedSegmentTupleProvider(TuplesProviderABC):
    def __init__(self, cacheController: SegmentCacheController):
        self._cacheController = cacheController

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        modelSetKey = tupleSelector.selector["modelSetKey"]
        keys = tupleSelector.selector["keys"]

        keysByChunkKey = defaultdict(list)

        foundDocuments: List[GraphDbPackedSegmentTuple] = []

        for key in keys:
            keysByChunkKey[makeChunkKeyForSegmentKey(modelSetKey, key)].append(key)

        for chunkKey, subKeys in keysByChunkKey.items():
            chunk: GraphDbEncodedChunkTuple = self._cacheController.segmentChunk(chunkKey)

            if not chunk:
                logger.warning("GraphDb segment chunk %s is missing from cache", chunkKey)
                continue

            segmentsByKeyStr = Payload().fromEncodedPayload(chunk.encodedData).tuples[0]
            segmentsByKey = json.loads(segmentsByKeyStr)

            for subKey in subKeys:
                if subKey not in segmentsByKey:
                    logger.warning(
                        "Document %s is missing from index, chunkKey %s",
                        subKey, chunkKey
                    )
                    continue

                # Create the new object
                foundDocuments.append(GraphDbPackedSegmentTuple(
                    key=subKey,
                    packedJson=segmentsByKey[subKey]
                ))

        # Create the vortex message
        return Payload(filt, tuples=foundDocuments).makePayloadEnvelope().toVortexMsg()
