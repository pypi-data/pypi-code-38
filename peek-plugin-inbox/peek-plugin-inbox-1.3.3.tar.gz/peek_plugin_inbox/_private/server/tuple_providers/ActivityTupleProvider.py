import logging
from typing import Union

from twisted.internet.defer import Deferred

from peek_plugin_inbox._private.storage.Activity import Activity
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)


class ActivityTupleProvider(TuplesProviderABC):
    def __init__(self, ormSessionCreator):
        self._ormSessionCreator = ormSessionCreator

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        userId = tupleSelector.selector["userId"]

        session = self._ormSessionCreator()
        try:
            tasks = session.query(Activity).filter(Activity.userId == userId).all()

            # Create the vortex message
            msg = Payload(filt, tuples=tasks).makePayloadEnvelope().toVortexMsg()

        finally:
            session.close()

        return msg
