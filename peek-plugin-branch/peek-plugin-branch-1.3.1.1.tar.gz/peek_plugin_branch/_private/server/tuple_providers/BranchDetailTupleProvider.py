import logging
from typing import Union

from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_plugin_branch._private.storage.BranchDetailTable import BranchDetailTable

logger = logging.getLogger(__name__)


class BranchDetailTupleProvider(TuplesProviderABC):
    def __init__(self, ormSessionCreator):
        self._ormSessionCreator = ormSessionCreator

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        modelSetKey = tupleSelector.selector["modelSetKey"]

        session = self._ormSessionCreator()
        try:
            ormItems = session.query(BranchDetailTable) \
                .filter(BranchDetailTable.modelSetKey == modelSetKey) \
                .all()

            items = [o.toTuple() for o in ormItems]

            # Create the vortex message
            return Payload(filt, tuples=items).makePayloadEnvelope().toVortexMsg()

        finally:
            session.close()
