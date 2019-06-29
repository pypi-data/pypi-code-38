import logging
from typing import Union

from sqlalchemy.orm import joinedload
from twisted.internet.defer import Deferred

from peek_plugin_diagram._private.storage.Display import DispLevel
from peek_plugin_diagram._private.storage.ModelSet import ModelCoordSet
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.Tuple import TUPLE_TYPES_BY_NAME
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)

class ServerLookupTupleProvider(TuplesProviderABC):
    def __init__(self, ormSessionCreator):
        self._ormSessionCreator = ormSessionCreator

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        session = self._ormSessionCreator()
        try:
            Lookup = TUPLE_TYPES_BY_NAME[tupleSelector.name]

            if Lookup == DispLevel:
                all = (session.query(DispLevel)
                       .options(joinedload(DispLevel.coordSet)
                                .joinedload(ModelCoordSet.modelSet))
                       .all())

                for item in all:
                    item.data = {"modelSetKey": item.coordSet.modelSet.key}

            else:
                all = (session.query(Lookup)
                       .options(joinedload(Lookup.modelSet))
                       .all())

                for item in all:
                    item.data = {"modelSetKey": item.modelSet.key}

            return Payload(filt, tuples=all).makePayloadEnvelope().toVortexMsg()

        finally:
            session.close()
