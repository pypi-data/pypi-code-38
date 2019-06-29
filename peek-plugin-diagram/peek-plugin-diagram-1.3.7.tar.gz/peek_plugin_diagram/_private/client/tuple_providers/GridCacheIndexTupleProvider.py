import logging
from typing import Union

from twisted.internet.defer import Deferred, inlineCallbacks

from peek_plugin_diagram._private.client.controller.GridCacheController import \
    GridCacheController
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)


class GridCacheIndexTupleProvider(TuplesProviderABC):
    def __init__(self, gridCacheController: GridCacheController):
        self._gridCacheController = gridCacheController

    @inlineCallbacks
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        tuples = [
            [i[0], i[1]]
            for i in self._gridCacheController.gridDatesByKey().items()
        ]
        sorted(tuples, key=lambda i: i[0])

        start = tupleSelector.selector.get('start')
        count = tupleSelector.selector.get('count')

        if start is not None and count:
            tuples = tuples[start:count]

        payloadEnvelope = yield Payload(filt, tuples=tuples).makePayloadEnvelopeDefer()
        vortexMsg = yield payloadEnvelope.toVortexMsgDefer()
        return vortexMsg
