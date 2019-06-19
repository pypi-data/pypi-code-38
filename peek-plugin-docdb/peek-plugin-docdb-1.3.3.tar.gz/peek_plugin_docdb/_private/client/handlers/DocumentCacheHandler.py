import logging
from collections import defaultdict
from typing import List, Dict

from twisted.internet.defer import DeferredList, inlineCallbacks, Deferred

from peek_plugin_docdb._private.PluginNames import docDbFilt
from peek_plugin_docdb._private.client.controller.DocumentCacheController import \
    DocumentCacheController
from peek_plugin_docdb._private.tuples.DocumentUpdateDateTuple import \
    DocumentUpdateDateTuple
from vortex.DeferUtil import vortexLogFailure
from vortex.Payload import Payload
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.PayloadEnvelope import PayloadEnvelope
from vortex.VortexABC import SendVortexMsgResponseCallable
from vortex.VortexFactory import VortexFactory

logger = logging.getLogger(__name__)

clientDocumentWatchUpdateFromDeviceFilt = {
    'key': "clientDocumentWatchUpdateFromDevice"
}
clientDocumentWatchUpdateFromDeviceFilt.update(docDbFilt)


# ModelSet HANDLER
class DocumentCacheHandler(object):
    def __init__(self, cacheController: DocumentCacheController,
                 clientId: str):
        """ App Document Handler

        This class handles the custom needs of the desktop/mobile apps observing documents.

        """
        self._cacheController = cacheController
        self._clientId = clientId

        self._epObserve = PayloadEndpoint(
            clientDocumentWatchUpdateFromDeviceFilt, self._processObserve
        )

        self._uuidsObserving = set()

    def shutdown(self):
        self._epObserve.shutdown()
        self._epObserve = None

    # ---------------
    # Process update from the server

    def notifyOfDocumentUpdate(self, chunkKeys: List[str]):
        """ Notify of Document Updates

        This method is called by the client.DocumentCacheController when it receives updates
        from the server.

        """
        vortexUuids = set(VortexFactory.getRemoteVortexUuids()) & self._uuidsObserving
        self._uuidsObserving = vortexUuids

        payloadsByVortexUuid = defaultdict(Payload)

        for chunkKey in chunkKeys:
            encodedDocumentChunk = self._cacheController.documentChunk(chunkKey)

            # Queue up the required client notifications
            for vortexUuid in vortexUuids:
                logger.debug("Sending unsolicited document %s to vortex %s",
                             chunkKey, vortexUuid)
                payloadsByVortexUuid[vortexUuid].tuples.append(encodedDocumentChunk)

        # Send the updates to the clients
        dl = []
        for vortexUuid, payload in list(payloadsByVortexUuid.items()):
            payload.filt = clientDocumentWatchUpdateFromDeviceFilt

            # Serialise in thread, and then send.
            d = payload.makePayloadEnvelopeDefer()
            d.addCallback(lambda payloadEnvelope: payloadEnvelope.toVortexMsgDefer())
            d.addCallback(VortexFactory.sendVortexMsg, destVortexUuid=vortexUuid)
            dl.append(d)

        # Log the errors, otherwise we don't care about them
        dl = DeferredList(dl, fireOnOneErrback=True)
        dl.addErrback(vortexLogFailure, logger, consumeError=True)

    # ---------------
    # Process observes from the devices
    @inlineCallbacks
    def _processObserve(self, payloadEnvelope: PayloadEnvelope,
                        vortexUuid: str,
                        sendResponse: SendVortexMsgResponseCallable,
                        **kwargs):

        payload = yield payloadEnvelope.decodePayloadDefer()

        updateDatesTuples: DocumentUpdateDateTuple = payload.tuples[0]

        self._uuidsObserving.add(vortexUuid)

        yield self._replyToObserve(payload.filt,
                                   updateDatesTuples.updateDateByChunkKey,
                                   sendResponse,
                                   vortexUuid)

    # ---------------
    # Reply to device observe

    @inlineCallbacks
    def _replyToObserve(self, filt,
                        lastUpdateByDocumentKey: Dict[str, str],
                        sendResponse: SendVortexMsgResponseCallable,
                        vortexUuid: str) -> None:
        """ Reply to Observe

        The client has told us that it's observing a new set of documents, and the lastUpdate
        it has for each of those documents. We will send them the documents that are out of date
        or missing.

        :param filt: The payload filter to respond to.
        :param lastUpdateByDocumentKey: The dict of documentKey:lastUpdate
        :param sendResponse: The callable provided by the Vortex (handy)
        :returns: None

        """
        yield None

        documentTuplesToSend = []

        # Check and send any updates
        for documentKey, lastUpdate in lastUpdateByDocumentKey.items():
            if vortexUuid not in VortexFactory.getRemoteVortexUuids():
                logger.debug("Vortex %s is offline, stopping update")
                return

            # NOTE: lastUpdate can be null.
            encodedDocumentTuple = self._cacheController.documentChunk(documentKey)
            if not encodedDocumentTuple:
                logger.debug("Document %s is not in the cache" % documentKey)
                continue

            # We are king, If it's it's not our version, it's the wrong version ;-)
            logger.debug("%s, %s,  %s",
                         encodedDocumentTuple.lastUpdate == lastUpdate,
                         encodedDocumentTuple.lastUpdate, lastUpdate)

            if encodedDocumentTuple.lastUpdate == lastUpdate:
                logger.debug("Document %s matches the cache" % documentKey)
                continue

            documentTuplesToSend.append(encodedDocumentTuple)
            logger.debug("Sending document %s from the cache" % documentKey)

        # Send the payload to the frontend
        payload = Payload(filt=filt, tuples=documentTuplesToSend)
        d: Deferred = payload.makePayloadEnvelopeDefer()
        d.addCallback(lambda payloadEnvelope: payloadEnvelope.toVortexMsgDefer())
        d.addCallback(sendResponse)
        d.addErrback(vortexLogFailure, logger, consumeError=True)
