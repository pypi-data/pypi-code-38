import logging
from collections import defaultdict
from typing import Dict, List

from twisted.internet.defer import inlineCallbacks

from peek_plugin_index_blueprint._private.PluginNames import indexBlueprintFilt
from peek_plugin_index_blueprint._private.server.client_handlers.ThingIndexChunkLoadRpc import \
    ThingIndexChunkLoadRpc
from peek_plugin_index_blueprint._private.storage.ThingIndexEncodedChunk import \
    ThingIndexEncodedChunk
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.PayloadEnvelope import PayloadEnvelope

logger = logging.getLogger(__name__)

clientThingIndexUpdateFromServerFilt = dict(key="clientThingIndexUpdateFromServer")
clientThingIndexUpdateFromServerFilt.update(indexBlueprintFilt)


class ThingIndexCacheController:
    """ ThingIndex Cache Controller

    The ThingIndex cache controller stores all the chunks in memory,
    allowing fast access from the mobile and desktop devices.

    """

    LOAD_CHUNK = 32

    def __init__(self, clientId: str):
        self._clientId = clientId
        self._webAppHandler = None

        #: This stores the cache of thingIndex data for the clients
        self._cache: Dict[int, ThingIndexEncodedChunk] = {}

        self._endpoint = PayloadEndpoint(clientThingIndexUpdateFromServerFilt,
                                         self._processThingIndexPayload)

    def setThingIndexCacheHandler(self, handler):
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
                "Loading ThingIndexChunk %s to %s" % (offset, offset + self.LOAD_CHUNK))
            encodedChunkTuples: List[ThingIndexEncodedChunk] = (
                yield ThingIndexChunkLoadRpc.loadThingIndexChunks(offset, self.LOAD_CHUNK)
            )

            if not encodedChunkTuples:
                break

            self._loadThingIndexIntoCache(encodedChunkTuples)

            offset += self.LOAD_CHUNK

    @inlineCallbacks
    def _processThingIndexPayload(self, payloadEnvelope: PayloadEnvelope, **kwargs):
        paylod = yield payloadEnvelope.decodePayloadDefer()
        thingIndexTuples: List[ThingIndexEncodedChunk] = paylod.tuples
        self._loadThingIndexIntoCache(thingIndexTuples)

    def _loadThingIndexIntoCache(self,
                                  encodedChunkTuples: List[ThingIndexEncodedChunk]):
        chunkKeysUpdated: List[str] = []

        for t in encodedChunkTuples:

            if (not t.chunkKey in self._cache or
                    self._cache[t.chunkKey].lastUpdate != t.lastUpdate):
                self._cache[t.chunkKey] = t
                chunkKeysUpdated.append(t.chunkKey)

        logger.debug("Received thingIndex updates from server, %s", chunkKeysUpdated)

        self._webAppHandler.notifyOfThingIndexUpdate(chunkKeysUpdated)

    def thingIndexChunk(self, chunkKey) -> ThingIndexEncodedChunk:
        return self._cache.get(chunkKey)

    def thingIndexKeys(self) -> List[int]:
        return list(self._cache)
