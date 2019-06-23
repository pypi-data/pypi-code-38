import logging
from typing import List, Optional

from peek_plugin_docdb._private.client.controller.DocumentCacheController import \
    clientDocumentUpdateFromServerFilt
from twisted.internet.defer import Deferred

from peek_plugin_base.PeekVortexUtil import peekClientName
from peek_plugin_docdb._private.storage.DocDbEncodedChunk import DocDbEncodedChunk
from vortex.DeferUtil import vortexLogFailure, deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.VortexFactory import VortexFactory, NoVortexException

logger = logging.getLogger(__name__)


class ClientChunkUpdateHandler:
    """ Client Document Update Controller

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

    def sendChunks(self, chunkKeys: List[str]) -> None:
        """ Send Location Indexes

        Send grid updates to the client services

        :param chunkKeys: A list of object buckets that have been updated
        :returns: Nothing
        """

        if not chunkKeys:
            return

        if peekClientName not in VortexFactory.getRemoteVortexName():
            logger.debug("No clients are online to send the doc chunk to, %s", chunkKeys)
            return

        def send(vortexMsg: bytes):
            if vortexMsg:
                VortexFactory.sendVortexMsg(
                    vortexMsg, destVortexName=peekClientName
                )

        d: Deferred = self._loadChunks(chunkKeys)
        d.addCallback(send)
        d.addErrback(self._sendErrback, chunkKeys)

    def _sendErrback(self, failure, chunkKeys):

        if failure.check(NoVortexException):
            logger.debug(
                "No clients are online to send the doc chunk to, %s", chunkKeys)
            return

        vortexLogFailure(failure, logger)

    @deferToThreadWrapWithLogger(logger)
    def _loadChunks(self, chunkKeys: List[str]) -> Optional[bytes]:

        session = self._dbSessionCreator()
        try:
            results = list(
                session.query(DocDbEncodedChunk)
                    .filter(DocDbEncodedChunk.chunkKey.in_(chunkKeys))
            )

            if not results:
                return None

            return (
                Payload(filt=clientDocumentUpdateFromServerFilt, tuples=results)
                    .makePayloadEnvelope().toVortexMsg()
            )

        finally:
            session.close()
