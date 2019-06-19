import logging

from txhttputil.util.DeferUtil import deferToThreadWrap
from typing import Union

from twisted.internet.defer import Deferred

from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

from peek_plugin_livedb._private.storage.StringIntTuple import StringIntTuple

logger = logging.getLogger(__name__)

class StringIntTupleProvider(TuplesProviderABC):
    def __init__(self, ormSessionCreator):
        self._ormSessionCreator = ormSessionCreator

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        # Potential filters can be placed here.
        # val1 = tupleSelector.selector["val1"]

        session = self._ormSessionCreator()
        try:
            tasks = (session.query(StringIntTuple)
                # Potentially filter the results
                # .filter(StringIntTuple.val1 == val1)
                .all()
            )

            # Create the vortex message
            return Payload(filt, tuples=tasks).makePayloadEnvelope().toVortexMsg()

        finally:
            session.close()
