import logging
from typing import Union

from twisted.internet.defer import Deferred, inlineCallbacks

from peek_plugin_graphdb._private.client.controller.ItemKeyIndexCacheController import \
    ItemKeyIndexCacheController
from peek_plugin_graphdb._private.tuples.ItemKeyIndexUpdateDateTuple import \
    ItemKeyIndexUpdateDateTuple
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)


class ItemKeyIndexUpdateDateTupleProvider(TuplesProviderABC):
    def __init__(self, cacheHandler: ItemKeyIndexCacheController):
        self._cacheHandler = cacheHandler

    @inlineCallbacks
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        tuple_ = ItemKeyIndexUpdateDateTuple()
        tuple_.updateDateByChunkKey = {
            key:self._cacheHandler.itemKeyIndexChunk(key).lastUpdate
            for key in self._cacheHandler.itemKeyIndexKeys()
        }
        payload = Payload(filt, tuples=[tuple_])
        payloadEnvelope = yield payload.makePayloadEnvelopeDefer()
        vortexMsg = yield payloadEnvelope.toVortexMsg()
        return vortexMsg
