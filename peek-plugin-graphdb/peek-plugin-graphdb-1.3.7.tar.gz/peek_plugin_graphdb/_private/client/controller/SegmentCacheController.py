import logging
from collections import defaultdict
from typing import Dict, List

from peek_plugin_graphdb._private.PluginNames import graphDbFilt
from peek_plugin_graphdb._private.server.client_handlers.SegmentIndexChunkLoadRpc import \
    SegmentIndexChunkLoadRpc
from peek_plugin_graphdb._private.tuples.GraphDbEncodedChunkTuple import \
    GraphDbEncodedChunkTuple
from twisted.internet.defer import inlineCallbacks
from vortex.DeferUtil import vortexLogFailure
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.PayloadEnvelope import PayloadEnvelope

logger = logging.getLogger(__name__)

clientSegmentUpdateFromServerFilt = dict(key="clientSegmentUpdateFromServer")
clientSegmentUpdateFromServerFilt.update(graphDbFilt)


class SegmentCacheController:
    """ Segment Cache Controller

    The Segment cache controller stores all the chunks in memory,
    allowing fast access from the mobile and desktop devices.

    """

    LOAD_CHUNK = 32

    def __init__(self, clientId: str):
        self._clientId = clientId
        self._webAppHandler = None
        self._fastGraphDb = None

        #: This stores the cache of segment data for the clients
        self._cache: Dict[str, GraphDbEncodedChunkTuple] = {}

        self._endpoint = PayloadEndpoint(clientSegmentUpdateFromServerFilt,
                                         self._processSegmentPayload)

    def setSegmentCacheHandler(self, handler):
        self._webAppHandler = handler

    def setFastGraphDb(self, fastGraphDb):
        self._fastGraphDb = fastGraphDb

    @inlineCallbacks
    def start(self):
        yield self.reloadCache()

    def shutdown(self):
        self._tupleObservable = None

        self._endpoint.shutdown()
        self._endpoint = None

        self._cache = {}

    @inlineCallbacks
    def reloadCache(self):
        self._cache = {}

        offset = 0
        while True:
            logger.info(
                "Loading SegmentChunk %s to %s" % (offset, offset + self.LOAD_CHUNK))
            encodedChunkTuples: List[GraphDbEncodedChunkTuple] = (
                yield SegmentIndexChunkLoadRpc.loadSegmentChunks(offset, self.LOAD_CHUNK)
            )

            if not encodedChunkTuples:
                break

            self._loadSegmentIntoCache(encodedChunkTuples)

            offset += self.LOAD_CHUNK

    @inlineCallbacks
    def _processSegmentPayload(self, payloadEnvelope: PayloadEnvelope, **kwargs):
        paylod = yield payloadEnvelope.decodePayloadDefer()
        segmentTuples: List[GraphDbEncodedChunkTuple] = paylod.tuples
        self._loadSegmentIntoCache(segmentTuples)

    def _loadSegmentIntoCache(self,
                              encodedChunkTuples: List[GraphDbEncodedChunkTuple]):
        chunkKeysUpdatedByModelSet: Dict[str, List[str]] = defaultdict(list)

        for t in encodedChunkTuples:

            if (not t.chunkKey in self._cache or
                    self._cache[t.chunkKey].lastUpdate != t.lastUpdate):
                self._cache[t.chunkKey] = t
                chunkKeysUpdatedByModelSet[t.modelSetKey].append(t.chunkKey)

        for modelSetKey, updatedChunkKeys in chunkKeysUpdatedByModelSet.items():
            logger.debug("Received segment updates from server, %s", updatedChunkKeys)

            d = self._webAppHandler.notifyOfSegmentUpdate(updatedChunkKeys)
            d.addErrback(vortexLogFailure, logger, consumeError=True)

            fastGraphDbModel = self._fastGraphDb.graphForModelSet(modelSetKey)
            d = fastGraphDbModel.notifyOfSegmentUpdate(updatedChunkKeys)
            d.addErrback(vortexLogFailure, logger, consumeError=True)

    def segmentChunk(self, chunkKey) -> GraphDbEncodedChunkTuple:
        return self._cache.get(chunkKey)

    def segmentKeys(self) -> List[str]:
        return list(self._cache)
