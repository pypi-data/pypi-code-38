import json
import logging
from typing import Dict, List

from peek_plugin_graphdb._private.PluginNames import graphDbFilt
from peek_plugin_graphdb._private.server.client_handlers.ItemKeyIndexChunkLoadRpc import \
    ItemKeyIndexChunkLoadRpc
from peek_plugin_graphdb._private.storage.ItemKeyIndexEncodedChunk import \
    ItemKeyIndexEncodedChunk
from peek_plugin_graphdb._private.worker.tasks._ItemKeyIndexCalcChunkKey import \
    makeChunkKeyForItemKey
from twisted.internet.defer import inlineCallbacks
from vortex.Payload import Payload
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.PayloadEnvelope import PayloadEnvelope

logger = logging.getLogger(__name__)

clientItemKeyIndexUpdateFromServerFilt = dict(key="clientItemKeyIndexUpdateFromServer")
clientItemKeyIndexUpdateFromServerFilt.update(graphDbFilt)


class ItemKeyIndexCacheController:
    """ ItemKeyIndex Cache Controller

    The ItemKeyIndex cache controller stores all the chunks in memory,
    allowing fast access from the mobile and desktop devices.

    """

    LOAD_CHUNK = 64

    def __init__(self, clientId: str):
        self._clientId = clientId
        self._webAppHandler = None

        #: This stores the cache of itemKeyIndex data for the clients
        self._cache: Dict[int, ItemKeyIndexEncodedChunk] = {}

        self._endpoint = PayloadEndpoint(clientItemKeyIndexUpdateFromServerFilt,
                                         self._processItemKeyIndexPayload)

    def setItemKeyIndexCacheHandler(self, handler):
        self._webAppHandler = handler

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
                "Loading ItemKeyIndexChunk %s to %s" % (offset, offset + self.LOAD_CHUNK))
            encodedChunkTuples: List[ItemKeyIndexEncodedChunk] = (
                yield ItemKeyIndexChunkLoadRpc.loadItemKeyIndexChunks(offset,
                                                                      self.LOAD_CHUNK)
            )

            if not encodedChunkTuples:
                break

            self._loadItemKeyIndexIntoCache(encodedChunkTuples)

            offset += self.LOAD_CHUNK

    @inlineCallbacks
    def _processItemKeyIndexPayload(self, payloadEnvelope: PayloadEnvelope, **kwargs):
        paylod = yield payloadEnvelope.decodePayloadDefer()
        itemKeyIndexTuples: List[ItemKeyIndexEncodedChunk] = paylod.tuples
        self._loadItemKeyIndexIntoCache(itemKeyIndexTuples)

    def _loadItemKeyIndexIntoCache(self,
                                   encodedChunkTuples: List[ItemKeyIndexEncodedChunk]):
        chunkKeysUpdated: List[str] = []

        for t in encodedChunkTuples:

            if (not t.chunkKey in self._cache or
                    self._cache[t.chunkKey].lastUpdate != t.lastUpdate):
                self._cache[t.chunkKey] = t
                chunkKeysUpdated.append(t.chunkKey)

        logger.debug("Received itemKeyIndex updates from server, %s", chunkKeysUpdated)

        self._webAppHandler.notifyOfItemKeyIndexUpdate(chunkKeysUpdated)

    def itemKeyIndexChunk(self, chunkKey) -> ItemKeyIndexEncodedChunk:
        return self._cache.get(chunkKey)

    def itemKeyIndexKeys(self) -> List[int]:
        return list(self._cache)

    def getSegmentKeys(self, modelSetKey: str, vertexKey: str) -> List[str]:

        chunkKey = makeChunkKeyForItemKey(modelSetKey, vertexKey)

        chunk: ItemKeyIndexEncodedChunk = (
            self.itemKeyIndexChunk(chunkKey)
        )

        if not chunk:
            logger.warning("ItemKeyIndex chunk %s is missing from cache", chunkKey)
            return []

        resultsByKeyStr = Payload().fromEncodedPayload(chunk.encodedData).tuples[0]
        resultsByKey = json.loads(resultsByKeyStr)

        if vertexKey not in resultsByKey:
            logger.warning(
                "ItemKey %s is missing from index, chunkKey %s",
                vertexKey, chunkKey
            )
            return []

        packedJson = resultsByKey[vertexKey]

        segmentKeys = json.loads(packedJson)

        return segmentKeys
