import logging
from collections import defaultdict
from typing import Union

from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_plugin_diagram._private.storage.branch.BranchIndex import BranchIndex
from peek_plugin_diagram._private.tuples.branch.BranchKeyToIdMapTuple import \
    BranchKeyToIdMapTuple

logger = logging.getLogger(__name__)


class BranchKeyToIdMapTupleProvider(TuplesProviderABC):
    def __init__(self, ormSessionCreator):
        self._ormSessionCreator = ormSessionCreator

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:

        session = self._ormSessionCreator()
        try:
            tuples = session.query(BranchIndex.id,
                                   BranchIndex.coordSetId,
                                   BranchIndex.key).all()

            tupleByCoordSetId = defaultdict(BranchKeyToIdMapTuple)
            for t in tuples:
                newTuple = tupleByCoordSetId[t.coordSetId]
                if not newTuple.keyIdMap:
                    newTuple.keyIdMap = {}
                newTuple.keyIdMap[t.key] = t.id
                newTuple.coordSetId = t.coordSetId

            return Payload(filt, tuples=list(tupleByCoordSetId.values())) \
                .makePayloadEnvelope().toVortexMsg()

        finally:
            session.close()
