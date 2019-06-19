import logging
from collections import defaultdict
from typing import Dict, List, Set, Optional

from peek_plugin_graphdb._private.PluginNames import graphDbFilt
from peek_plugin_graphdb._private.server.client_handlers.TraceConfigLoadRpc import \
    TraceConfigLoadRpc
from peek_plugin_graphdb.tuples.GraphDbTraceConfigTuple import \
    GraphDbTraceConfigTuple
from twisted.internet.defer import inlineCallbacks
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.PayloadEnvelope import PayloadEnvelope
from vortex.PayloadFilterKeys import plDeleteKey
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableProxyHandler import TupleDataObservableProxyHandler

logger = logging.getLogger(__name__)

clientTraceConfigUpdateFromServerFilt = dict(key="clientTraceConfigUpdateFromServer")
clientTraceConfigUpdateFromServerFilt.update(graphDbFilt)


class TraceConfigCacheController:
    """ TraceConfig Cache Controller

    The TraceConfig cache controller stores all the chunks in memory,
    allowing fast access from the mobile and desktop devices.

    """

    LOAD_CHUNK = 32

    def __init__(self, clientId: str, tupleObservable: TupleDataObservableProxyHandler):
        self._clientId = clientId
        self._tupleObservable = tupleObservable

        #: This stores the cache of segment data for the clients
        self._cache: Dict[str, Dict[str, GraphDbTraceConfigTuple]] = defaultdict(dict)

        self._endpoint = PayloadEndpoint(clientTraceConfigUpdateFromServerFilt,
                                         self._processTraceConfigPayload)

    @inlineCallbacks
    def start(self):
        yield self.reloadCache()

    def shutdown(self):
        self._tupleObservable = None

        self._endpoint.shutdown()
        self._endpoint = None

        self._cache = defaultdict(dict)

    @inlineCallbacks
    def reloadCache(self):
        self._cache = defaultdict(dict)

        offset = 0
        while True:
            logger.info(
                "Loading TraceConfig %s to %s" % (offset, offset + self.LOAD_CHUNK)
            )
            traceConfigTuples: List[GraphDbTraceConfigTuple] = (
                yield TraceConfigLoadRpc.loadTraceConfigs(offset, self.LOAD_CHUNK)
            )

            if not traceConfigTuples:
                break

            traceConfigsByModelSetKey = defaultdict(list)
            for trace in traceConfigTuples:
                traceConfigsByModelSetKey[trace.modelSetKey].append(trace)

            del traceConfigTuples

            for modelSetKey, traceConfigTuples in traceConfigsByModelSetKey.items():
                self._loadTraceConfigIntoCache(modelSetKey, traceConfigTuples)

            offset += self.LOAD_CHUNK

    @inlineCallbacks
    def _processTraceConfigPayload(self, payloadEnvelope: PayloadEnvelope, **kwargs):
        payload = yield payloadEnvelope.decodePayloadDefer()

        dataDict = payload.tuples[0]

        if payload.filt.get(plDeleteKey):
            modelSetKey = dataDict["modelSetKey"]
            traceConfigKeys = dataDict["traceConfigKeys"]
            self._removeTraceConfigFromCache(modelSetKey, traceConfigKeys)
            return

        modelSetKey = dataDict["modelSetKey"]

        traceConfigTuples: List[GraphDbTraceConfigTuple] = dataDict["tuples"]
        self._loadTraceConfigIntoCache(modelSetKey, traceConfigTuples)

    def _removeTraceConfigFromCache(self, modelSetKey: str, traceConfigKeys: List[str]):
        subCache = self._cache[modelSetKey]

        logger.debug("Received TraceConfig deletes from server, %s %s removed",
                     modelSetKey, len(traceConfigKeys))

        for traceConfigKey in traceConfigKeys:
            if traceConfigKey in subCache:
                subCache.pop(traceConfigKey)

        self._tupleObservable.notifyOfTupleUpdate(
            TupleSelector(GraphDbTraceConfigTuple.tupleType(),
                          dict(modelSetKey=modelSetKey))
        )

    def _loadTraceConfigIntoCache(self, modelSetKey: str,
                                  traceConfigTuples: List[GraphDbTraceConfigTuple],
                                  deletedTraceConfigKeys: Set[str] = set()):
        subCache = self._cache[modelSetKey]

        traceKeysUpdated: Set[str] = {
            traceConfig.key for traceConfig in traceConfigTuples
        }

        deletedTraceConfigKeys -= traceKeysUpdated

        for traceConfig in traceConfigTuples:
            subCache[traceConfig.key] = traceConfig

        for traceConfigKey in deletedTraceConfigKeys:
            if traceConfigKey in subCache:
                subCache.pop(traceConfigKey)

        logger.debug("Received TraceConfig updates from server,"
                     "%s %s removed, %s added/updated",
                     modelSetKey, len(deletedTraceConfigKeys), len(traceKeysUpdated))

        self._tupleObservable.notifyOfTupleUpdate(
            TupleSelector(GraphDbTraceConfigTuple.tupleType(),
                          dict(modelSetKey=modelSetKey))
        )

    def traceConfigTuple(self, modelSetKey: str,
                         traceConfigKey: str) -> GraphDbTraceConfigTuple:
        return self._cache[modelSetKey][traceConfigKey]

    def traceConfigTuples(self, modelSetKey: Optional[str]
                          ) -> List[GraphDbTraceConfigTuple]:
        if modelSetKey:
            return list(self._cache[modelSetKey].values())

        configs = []
        for configsByKey in self._cache.values():
            configs += configsByKey.values()
        return configs
