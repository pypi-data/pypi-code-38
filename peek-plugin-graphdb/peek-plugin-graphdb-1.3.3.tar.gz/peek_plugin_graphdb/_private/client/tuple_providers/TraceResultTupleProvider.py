import logging
from typing import Union

from peek_plugin_graphdb._private.client.controller.TracerController import \
    TracerController
from twisted.internet.defer import Deferred, inlineCallbacks
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)


class TraceResultTupleProvider(TuplesProviderABC):
    def __init__(self, tracerController: TracerController):
        self._tracerController = tracerController

    @inlineCallbacks
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        modelSetKey = tupleSelector.selector["modelSetKey"]
        startVertexKey = tupleSelector.selector["startVertexKey"]
        traceConfigKey = tupleSelector.selector["traceConfigKey"]

        traceResult = yield self._tracerController.runTrace(
            modelSetKey, traceConfigKey, startVertexKey
        )

        envelope = yield Payload(filt, tuples=[traceResult]).makePayloadEnvelopeDefer()
        vortexMsg = yield envelope.toVortexMsgDefer()
        return vortexMsg
