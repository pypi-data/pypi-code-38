import logging
from typing import Union, Optional

from twisted.internet.defer import Deferred, inlineCallbacks
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_plugin_diagram._private.client.controller.GridCacheController import \
    GridCacheController
from peek_plugin_diagram._private.storage.ModelSet import makeDispGroupGridKey
from peek_plugin_diagram._private.tuples.GroupDispsTuple import GroupDispsTuple
from peek_plugin_diagram._private.tuples.grid.EncodedGridTuple import EncodedGridTuple

logger = logging.getLogger(__name__)


class ClientGroupDispsTupleProvider(TuplesProviderABC):
    def __init__(self, gridCacheController: GridCacheController):
        self.gridCacheController = gridCacheController

    @inlineCallbacks
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        coordSetId = tupleSelector.selector['coordSetId']
        gridKey = makeDispGroupGridKey(coordSetId)
        grid: Optional[EncodedGridTuple] = self.gridCacheController.grid(gridKey)

        groupDispTuple = GroupDispsTuple()
        groupDispTuple.coordSetId = coordSetId
        groupDispTuple.encodedGridTuple = grid.encodedGridTuple if grid else None

        payloadEnvelope = yield Payload(filt, tuples=[groupDispTuple]) \
            .makePayloadEnvelopeDefer()

        vortexMsg = yield payloadEnvelope.toVortexMsgDefer()
        return vortexMsg

