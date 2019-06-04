import logging
from typing import Union

from twisted.internet.defer import Deferred

from peek_core_device._private.storage.DeviceInfoTuple import DeviceInfoTuple
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)

class DeviceInfoTupleProvider(TuplesProviderABC):
    def __init__(self, ormSessionCreator):
        self._ormSessionCreator = ormSessionCreator

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:

        deviceId = tupleSelector.selector.get("deviceId")

        ormSession = self._ormSessionCreator()
        try:
            qry = ormSession.query(DeviceInfoTuple)

            if deviceId is not None:
                qry = qry.filter(DeviceInfoTuple.deviceId == deviceId)

            tuples = qry.all()

            # Create the vortex message
            return Payload(filt, tuples=tuples).makePayloadEnvelope().toVortexMsg()

        finally:
            ormSession.close()
