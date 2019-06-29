from typing import Union

from twisted.internet.defer import Deferred
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_plugin_diagram_generic_menu._private.storage.DiagramGenericMenuTuple import \
    DiagramGenericMenuTuple

import logging
from vortex.DeferUtil import deferToThreadWrapWithLogger

logger = logging.getLogger(__name__)

class DiagramGenericMenuTupleProvider(TuplesProviderABC):
    def __init__(self, ormSessionCreator):
        self._ormSessionCreator = ormSessionCreator

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:

        session = self._ormSessionCreator()
        try:
            tuples = session.query(DiagramGenericMenuTuple).all()

            # Create the vortex message
            return Payload(filt, tuples=tuples).makePayloadEnvelope().toVortexMsg()

        finally:
            session.close()
