import logging
from twisted.internet.defer import Deferred
from typing import Union
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_plugin_graphdb._private.client.controller.TraceConfigCacheController import \
    TraceConfigCacheController

logger = logging.getLogger(__name__)


class TraceConfigTupleProvider(TuplesProviderABC):
    def __init__(self, cacheHandler: TraceConfigCacheController):
        self._cacheHandler = cacheHandler

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        # the UI doesn't supply the model set at present.
        modelSetKey = tupleSelector.selector.get("modelSetKey")

        data = self._cacheHandler.traceConfigTuples(modelSetKey=modelSetKey)

        # Create the vortex message
        return Payload(filt, tuples=data).makePayloadEnvelope().toVortexMsg()
