import logging
from copy import copy
from typing import List, Optional

from sqlalchemy.orm import joinedload
from twisted.internet.defer import Deferred, inlineCallbacks
from vortex.DeferUtil import vortexLogFailure, deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.PayloadFilterKeys import plDeleteKey
from vortex.VortexFactory import VortexFactory, NoVortexException

from peek_plugin_base.PeekVortexUtil import peekClientName
from peek_plugin_graphdb._private.client.controller.TraceConfigCacheController import \
    clientTraceConfigUpdateFromServerFilt
from peek_plugin_graphdb._private.storage.GraphDbModelSet import GraphDbModelSet
from peek_plugin_graphdb._private.storage.GraphDbTraceConfig import GraphDbTraceConfig

logger = logging.getLogger(__name__)


class TraceConfigUpdateHandler:
    """ Client Segment Update Controller

    This controller handles sending updates the the client.

    It uses lower level Vortex API

    It does the following a broadcast to all clients:

    1) Sends grid updates to the clients

    2) Sends Lookup updates to the clients

    """

    def __init__(self, dbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

    def shutdown(self):
        pass

    @inlineCallbacks
    def sendDeleted(self, modelSetKey: str, traceConfigKeys: List[str]) -> None:
        """ Send Deleted

        Send grid updates to the client services

        :param modelSetKey: The model set key
        :param traceConfigKeys: A list of object buckets that have been updated
        :returns: Nothing
        """

        if not traceConfigKeys:
            return

        if peekClientName not in VortexFactory.getRemoteVortexName():
            logger.debug("No clients are online to send the doc chunk to, %s",
                         traceConfigKeys)
            return

        payload = Payload(filt=copy(clientTraceConfigUpdateFromServerFilt))
        payload.filt[plDeleteKey] = True
        payload.tuples = dict(modelSetKey=modelSetKey,
                              traceConfigKeys=traceConfigKeys)

        payloadEnvelope = yield payload.makePayloadEnvelopeDefer()
        vortexMsg = yield payloadEnvelope.toVortexMsgDefer()

        try:
            VortexFactory.sendVortexMsg(vortexMsg, destVortexName=peekClientName)

        except Exception as e:
            logger.exception(e)

    def sendCreatedOrUpdatedUpdates(self, modelSetKey: str,
                                    traceConfigKeys: List[str]) -> None:
        """ Send Create or Updated Updates

        Send grid updates to the client services

        :param modelSetKey: The model set key
        :param traceConfigKeys: A list of the keys updated
        :returns: Nothing
        """

        if not traceConfigKeys:
            return

        if peekClientName not in VortexFactory.getRemoteVortexName():
            logger.debug("No clients are online to send the trace configs to, %s",
                         traceConfigKeys)
            return

        def send(vortexMsg: bytes):
            if vortexMsg:
                VortexFactory.sendVortexMsg(
                    vortexMsg, destVortexName=peekClientName
                )

        d: Deferred = self._loadTraceConfigs(modelSetKey, traceConfigKeys)
        d.addCallback(send)
        d.addErrback(self._sendErrback, traceConfigKeys)

    def _sendErrback(self, failure, traceConfigKeys):

        if failure.check(NoVortexException):
            logger.debug(
                "No clients are online to send the doc chunk to, %s", traceConfigKeys)
            return

        vortexLogFailure(failure, logger)

    @deferToThreadWrapWithLogger(logger)
    def _loadTraceConfigs(self, modelSetKey: str, traceConfigKeys: List[str]
                          ) -> Optional[bytes]:

        session = self._dbSessionCreator()
        try:
            results = list(
                session.query(GraphDbTraceConfig)
                    .options(joinedload(GraphDbTraceConfig.modelSet))
                    .options(joinedload(GraphDbTraceConfig.rules))
                    .filter(GraphDbTraceConfig.key.in_(traceConfigKeys))
                    .join(GraphDbModelSet,
                          GraphDbTraceConfig.modelSetId == GraphDbModelSet.id)
                    .filter(GraphDbModelSet.key == modelSetKey)
            )

            if not results:
                return None

            data = dict(tuples=[ormObj.toTuple() for ormObj in results],
                        modelSetKey=modelSetKey)
            return (
                Payload(filt=clientTraceConfigUpdateFromServerFilt, tuples=data)
                    .makePayloadEnvelope().toVortexMsg()
            )

        finally:
            session.close()
