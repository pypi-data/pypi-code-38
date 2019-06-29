import logging
from typing import Union

from peek_plugin_diagram_trace._private.storage.Setting import globalSetting
from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)


class SettingPropertyTupleProvider(TuplesProviderABC):
    def __init__(self, ormSessionCreator):
        self._ormSessionCreator = ormSessionCreator

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:

        session = self._ormSessionCreator()
        try:

            tuples = globalSetting(session).propertyObjects

            # Create the vortex message
            return Payload(filt, tuples=tuples).makePayloadEnvelope().toVortexMsg()

        finally:
            session.close()
