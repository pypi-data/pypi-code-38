import logging
from typing import Union

from twisted.internet.defer import Deferred

from peek_plugin_diagram._private.storage.ModelSet import ModelSet
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)

class ServerModelSetTupleProvider(TuplesProviderABC):
    def __init__(self, ormSessionCreator):
        self._ormSessionCreator = ormSessionCreator

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:

        session = self._ormSessionCreator()
        try:
            tuples = session.query(ModelSet).all()
            return Payload(filt, tuples=tuples).makePayloadEnvelope().toVortexMsg()

        finally:
            session.close()
