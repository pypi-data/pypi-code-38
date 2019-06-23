import logging
from typing import Union

from twisted.internet.defer import Deferred, inlineCallbacks

from peek_plugin_graphdb._private.client.controller.SegmentCacheController import \
    SegmentCacheController
from peek_plugin_graphdb._private.tuples.SegmentIndexUpdateDateTuple import \
    SegmentIndexUpdateDateTuple
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)


class SegmentUpdateDateTupleProvider(TuplesProviderABC):
    def __init__(self, cacheHandler: SegmentCacheController):
        self._cacheHandler = cacheHandler

    @inlineCallbacks
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        tuple_ = SegmentIndexUpdateDateTuple()
        tuple_.updateDateByChunkKey = {
            key:self._cacheHandler.segmentChunk(key).lastUpdate
            for key in self._cacheHandler.segmentKeys()
        }
        payload = Payload(filt, tuples=[tuple_])
        payloadEnvelope = yield payload.makePayloadEnvelopeDefer()
        vortexMsg = yield payloadEnvelope.toVortexMsg()
        return vortexMsg
