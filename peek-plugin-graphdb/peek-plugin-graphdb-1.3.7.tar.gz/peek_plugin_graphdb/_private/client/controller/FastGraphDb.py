""" Fast Graph DB

This module stores a memory resident model of a graph network.

"""
import json
import logging
from typing import Optional, List, Dict, Set

from twisted.internet.defer import inlineCallbacks
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload

from peek_plugin_graphdb._private.client.controller.SegmentCacheController import \
    SegmentCacheController
from peek_plugin_graphdb._private.tuples.GraphDbEncodedChunkTuple import \
    GraphDbEncodedChunkTuple
from peek_plugin_graphdb.tuples.GraphDbLinkedSegment import GraphDbLinkedSegment

logger = logging.getLogger(__name__)


class FastGraphDb:
    def __init__(self, cacheController: SegmentCacheController):
        self._cacheController = cacheController
        self._graphsByModelSetKey = {}

    def graphForModelSet(self, modelSetKey: str) -> 'FastGraphDbModel':
        if modelSetKey not in self._graphsByModelSetKey:
            self._graphsByModelSetKey[modelSetKey] = FastGraphDbModel(
                modelSetKey, self._cacheController
            )

        return self._graphsByModelSetKey[modelSetKey]

    def shutdown(self):
        self._cacheController = None
        for model in self._graphsByModelSetKey.values():
            model.shutdown()

        self._graphsByModelSetKey = {}


class FastGraphDbModel:
    def __init__(self, modelSetKey: str, cacheController: SegmentCacheController):
        self._cacheController = cacheController
        self._modelSetKey = modelSetKey
        self._segmentsByKey: Dict[str, GraphDbLinkedSegment] = {}
        self._segmentKeysByChunkKey: Dict[str, Set[str]] = {}

    def shutdown(self):
        self._cacheController = None
        self._segmentsByKey = {}
        self._segmentKeysByChunkKey = {}

    def getSegment(self, segmentKey: str) -> Optional[GraphDbLinkedSegment]:
        return self._segmentsByKey.get(segmentKey)

    @inlineCallbacks
    def notifyOfSegmentUpdate(self, chunkKeys: List[str]):
        """ Notify of Segment Updates

        This method is called by the client.SegmentCacheController when it receives
         updates from the server.

        """
        for chunkKey in chunkKeys:
            graphDbEncodedChunkTuple = self._cacheController.segmentChunk(chunkKey)

            segments = yield self._unpackSegmentsFromChunk(graphDbEncodedChunkTuple)
            segmentKeys = set([s.key for s in segments])

            if chunkKey in self._segmentKeysByChunkKey:
                # Old keys from this chunk
                segmentKeysToRemove = self._segmentKeysByChunkKey[chunkKey]
                # New keys from this chunk
                segmentKeysToRemove -= segmentKeys

                # Remove the segments that are no longer present in this chunk
                for key in segmentKeysToRemove:
                    self._segmentsByKey.pop(key)

            # Make note of the new segment keys in this chunk
            self._segmentKeysByChunkKey[chunkKey] = segmentKeys

            # Add or update the segments in the model
            for segment in segments:
                self._segmentsByKey[segment.key] = segment

    @deferToThreadWrapWithLogger(logger)
    def _unpackSegmentsFromChunk(self, encodedChunkTuple: GraphDbEncodedChunkTuple
                                 ) -> List[GraphDbLinkedSegment]:

        foundSegments: List[GraphDbLinkedSegment] = []

        segmentJsonStrByKeyStr = (
            Payload()
                .fromEncodedPayload(encodedChunkTuple.encodedData)
                .tuples[0]
        )

        segmentJsonStrByKey = json.loads(segmentJsonStrByKeyStr)

        for segmentKey, segmentJsonStr in segmentJsonStrByKey.items():
            # Reconstruct the data
            objectProps: {} = json.loads(segmentJsonStr)

            # Create the new object
            newObject = GraphDbLinkedSegment()
            newObject.unpackJson(objectProps, segmentKey, self._modelSetKey)
            foundSegments.append(newObject)

        return foundSegments
