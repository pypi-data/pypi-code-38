import logging
from typing import Dict, List

from twisted.internet.defer import inlineCallbacks

from peek_plugin_diagram._private.PluginNames import diagramFilt
from peek_plugin_diagram._private.server.client_handlers.ClientLocationIndexLoaderRpc import \
    ClientLocationIndexLoaderRpc
from peek_plugin_diagram._private.tuples.location_index.EncodedLocationIndexTuple import \
    EncodedLocationIndexTuple
from peek_plugin_diagram._private.tuples.location_index.LocationIndexTuple import \
    LocationIndexTuple
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.PayloadEnvelope import PayloadEnvelope

logger = logging.getLogger(__name__)

clientLocationIndexUpdateFromServerFilt = dict(key="clientLocationIndexUpdateFromServer")
clientLocationIndexUpdateFromServerFilt.update(diagramFilt)


class LocationIndexCacheController:
    """ Disp Key Cache Controller

    The locationIndex cache controller stores all the locationIndexs in memory, allowing fast access from
    the mobile and desktop devices.

    """

    LOAD_CHUNK = 50

    def __init__(self, clientId: str):
        self._clientId = clientId
        self._cacheHandler = None
        self._cache: Dict[str, EncodedLocationIndexTuple] = {}
        self._locationIndexKeys = set()

        self._endpoint = PayloadEndpoint(clientLocationIndexUpdateFromServerFilt,
                                         self._processLocationIndexPayload)

    def setLocationIndexCacheHandler(self, locationIndexCacheHandler):
        self._cacheHandler = locationIndexCacheHandler

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
        self._locationIndexKeys = set()

        offset = 0
        while True:
            logger.info("Loading LocationIndex %s to %s" % (
                offset, offset + self.LOAD_CHUNK))
            locationIndexTuples = yield ClientLocationIndexLoaderRpc.loadLocationIndexes(
                offset, self.LOAD_CHUNK)
            if not locationIndexTuples:
                break

            self._loadLocationIndexIntoCache(locationIndexTuples)

            offset += self.LOAD_CHUNK

    @inlineCallbacks
    def _processLocationIndexPayload(self, payloadEnvelope: PayloadEnvelope, **kwargs):
        paylod = yield payloadEnvelope.decodePayloadDefer()
        locationIndexTuples: List[LocationIndexTuple] = paylod.tuples
        self._loadLocationIndexIntoCache(locationIndexTuples)

    def _loadLocationIndexIntoCache(self, locationIndexTuples: List[LocationIndexTuple]):
        indexBucketsUpdated: List[str] = []

        for t in locationIndexTuples:
            self._locationIndexKeys.add(t.indexBucket)

            if (not t.indexBucket in self._cache or
                    self._cache[t.indexBucket].lastUpdate != t.lastUpdate):
                self._cache[t.indexBucket] = t
                indexBucketsUpdated.append(t.indexBucket)

        logger.debug("Received locationIndex updates from server, %s",
                     indexBucketsUpdated)

        self._cacheHandler.notifyOfLocationIndexUpdate(indexBucketsUpdated)

    def locationIndex(self, indexBucket) -> EncodedLocationIndexTuple:
        return self._cache.get(indexBucket)

    def locationIndexKeys(self) -> List[str]:
        return list(self._locationIndexKeys)
