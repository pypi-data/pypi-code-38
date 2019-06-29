from typing import Union

from peek_plugin_diagram.server.DiagramViewerApiABC import DiagramViewerApiABC
from peek_plugin_gis_diagram._private.PluginNames import gisDiagramModelSetName
from twisted.internet.defer import Deferred, inlineCallbacks

from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC


class CoordSetTupleProvider(TuplesProviderABC):
    def __init__(self, diagramPluginViewerApi: DiagramViewerApiABC):
        self._diagramPluginViewerApi = diagramPluginViewerApi

    @inlineCallbacks
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        coordSets = yield self._diagramPluginViewerApi.getCoordSets(
            modelSetKey=gisDiagramModelSetName
        )

        payloadEnvelope = yield Payload(filt, tuples=coordSets).makePayloadEnvelopeDefer()
        vortexMsg = yield payloadEnvelope.toVortexMsgDefer()
        return vortexMsg

