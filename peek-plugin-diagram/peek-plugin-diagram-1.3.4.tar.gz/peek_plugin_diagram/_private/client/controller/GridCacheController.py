import logging
from typing import Dict, List

from peek_plugin_diagram._private.PluginNames import diagramFilt
from peek_plugin_diagram._private.server.client_handlers.ClientGridLoaderRpc import \
    ClientGridLoaderRpc
from peek_plugin_diagram._private.tuples.grid.EncodedGridTuple import EncodedGridTuple
from peek_plugin_diagram._private.tuples.grid.GridTuple import GridTuple
from twisted.internet.defer import inlineCallbacks, Deferred
from vortex.DeferUtil import vortexLogFailure
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.PayloadEnvelope import PayloadEnvelope

logger = logging.getLogger(__name__)

clientGridUpdateFromServerFilt = dict(key="clientGridUpdateFromServer")
clientGridUpdateFromServerFilt.update(diagramFilt)

clientCoordSetUpdateFromServerFilt = dict(key="clientCoordSetUpdateFromServer")
clientCoordSetUpdateFromServerFilt.update(diagramFilt)


class GridCacheController:
    """ Grid Cache Controller

    The grid cache controller stores all the grids in memory, allowing fast access from
    the mobile and desktop devices.

    NOTE: The grid set endpoint triggers a reload, this is in the case when grid sets
    are enable or disabled. Perhaps the system should just be restarted instead.

    """

    #: This stores the cache of grid data for the clients
    _gridCache: Dict[str, GridTuple] = None

    LOAD_CHUNK = 75
    LOAD_PARALLELISM = 6

    def __init__(self, clientId: str):
        self._clientId = clientId
        self._gridCacheHandler = None
        self._gridCache: Dict[str, EncodedGridTuple] = {}

        self._gridEndpoint = PayloadEndpoint(clientGridUpdateFromServerFilt,
                                             self._processGridPayload)

        self._coordSetEndpoint = PayloadEndpoint(clientCoordSetUpdateFromServerFilt,
                                                 self._processCoordSetPayload)

    def setGridCacheHandler(self, gridCacheHandler):
        self._gridCacheHandler = gridCacheHandler

    @inlineCallbacks
    def start(self):
        yield self.reloadCache()

    def shutdown(self):
        self._tupleObservable = None

        self._gridEndpoint.shutdown()
        self._gridEndpoint = None

        self._coordSetEndpoint.shutdown()
        self._coordSetEndpoint = None

        self._gridCache = {}
        # self._cachedGridCoordSetIds = set()

    def reloadCache(self):
        self._gridCache = {}

        d = Deferred()

        class C:
            inProgress = self.LOAD_PARALLELISM

        def nextChunk():
            offset = 0
            while True:
                yield offset
                offset += self.LOAD_CHUNK

        nextChunkGen = nextChunk()

        def callback(gridTuples):
            if not gridTuples:
                C.inProgress -= 1
                if not C.inProgress:
                    d.callback(True)
                return

            self._loadGridIntoCache(gridTuples)
            load()

        def load():
            offset = next(nextChunkGen)
            logger.info("Loading grids %s to %s" %
                        (offset, offset + self.LOAD_CHUNK))
            d = ClientGridLoaderRpc.loadGrids(offset, self.LOAD_CHUNK)
            d.addCallback(callback)
            d.addErrback(vortexLogFailure, logger, consumeError=True)

        for _ in range(self.LOAD_PARALLELISM):
            load()

        return d

    @inlineCallbacks
    def _processGridPayload(self, payloadEnvelope: PayloadEnvelope, **kwargs):
        payload = yield payloadEnvelope.decodePayloadDefer()
        gridTuples: List[EncodedGridTuple] = payload.tuples
        return self._loadGridIntoCache(gridTuples)

    def _processCoordSetPayload(self, payloadEnvelope: PayloadEnvelope, **kwargs):
        d: Deferred = self.reloadCache()
        d.addErrback(vortexLogFailure, logger, consumeError=True)

    def _loadGridIntoCache(self, encodedGridTuples: List[EncodedGridTuple]):
        gridKeyUpdates: List[str] = []

        for t in encodedGridTuples:
            if (not t.gridKey in self._gridCache or
                    self._gridCache[t.gridKey].lastUpdate != t.lastUpdate):
                self._gridCache[t.gridKey] = t
                gridKeyUpdates.append(t.gridKey)

        logger.debug("Received %s grids from server,"
                     " %s had changed ",
                     len(encodedGridTuples), len(gridKeyUpdates))

        self._gridCacheHandler.notifyOfGridUpdate(gridKeyUpdates)

    def grid(self, gridKey) -> EncodedGridTuple:
        return self._gridCache.get(gridKey)

    def gridKeyList(self) -> List[str]:
        return list(self._gridCache.keys())

    def gridDatesByKey(self):
        return {g.gridKey: g.lastUpdate for g in self._gridCache.values()}
