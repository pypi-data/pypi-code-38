import logging
from typing import Union

from twisted.internet.defer import Deferred, inlineCallbacks

from peek_plugin_index_blueprint._private.client.controller.ThingIndexCacheController import \
    ThingIndexCacheController
from peek_plugin_index_blueprint._private.tuples.ThingIndexUpdateDateTuple import \
    ThingIndexUpdateDateTuple
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)


class ThingIndexUpdateDateTupleProvider(TuplesProviderABC):
    def __init__(self, cacheHandler: ThingIndexCacheController):
        self._cacheHandler = cacheHandler

    @inlineCallbacks
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        tuple_ = ThingIndexUpdateDateTuple()
        tuple_.updateDateByChunkKey = {
            key:self._cacheHandler.thingIndexChunk(key).lastUpdate
            for key in self._cacheHandler.thingIndexKeys()
        }
        payload = Payload(filt, tuples=[tuple_])
        payloadEnvelope = yield payload.makePayloadEnvelopeDefer()
        vortexMsg = yield payloadEnvelope.toVortexMsg()
        return vortexMsg
