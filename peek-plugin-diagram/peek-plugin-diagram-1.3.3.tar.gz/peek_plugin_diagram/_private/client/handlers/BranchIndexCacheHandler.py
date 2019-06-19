import logging
from collections import defaultdict
from typing import List, Dict

from twisted.internet.defer import DeferredList, inlineCallbacks, Deferred

from peek_plugin_diagram._private.PluginNames import diagramFilt
from peek_plugin_diagram._private.client.controller.BranchIndexCacheController import \
    BranchIndexCacheController
from peek_plugin_diagram._private.tuples.branch.BranchIndexUpdateDateTuple import \
    BranchIndexUpdateDateTuple
from vortex.DeferUtil import vortexLogFailure
from vortex.Payload import Payload
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.PayloadEnvelope import PayloadEnvelope
from vortex.VortexABC import SendVortexMsgResponseCallable
from vortex.VortexFactory import VortexFactory

logger = logging.getLogger(__name__)

clientBranchIndexWatchUpdateFromDeviceFilt = {
    'key': "clientBranchIndexWatchUpdateFromDevice"
}
clientBranchIndexWatchUpdateFromDeviceFilt.update(diagramFilt)


# ModelSet HANDLER
class BranchIndexCacheHandler(object):
    def __init__(self, cacheController: BranchIndexCacheController,
                 clientId: str):
        """ App BranchIndex Handler

        This class handles the custom needs of the desktop/mobile apps observing branchIndexs.

        """
        self._cacheController = cacheController
        self._clientId = clientId

        self._epObserve = PayloadEndpoint(
            clientBranchIndexWatchUpdateFromDeviceFilt, self._processObserve
        )

        self._uuidsObserving = set()

    def shutdown(self):
        self._epObserve.shutdown()
        self._epObserve = None

    # ---------------
    # Process update from the server

    def notifyOfBranchIndexUpdate(self, chunkKeys: List[str]):
        """ Notify of BranchIndex Updates

        This method is called by the client.BranchIndexCacheController when it receives updates
        from the server.

        """
        vortexUuids = set(VortexFactory.getRemoteVortexUuids()) & self._uuidsObserving
        self._uuidsObserving = vortexUuids

        payloadsByVortexUuid = defaultdict(Payload)

        for chunkKey in chunkKeys:
            encodedBranchIndexChunk = self._cacheController.branchIndexChunk(chunkKey)

            # Queue up the required client notifications
            for vortexUuid in vortexUuids:
                logger.debug("Sending unsolicited branchIndex %s to vortex %s",
                             chunkKey, vortexUuid)
                payloadsByVortexUuid[vortexUuid].tuples.append(encodedBranchIndexChunk)

        # Send the updates to the clients
        dl = []
        for vortexUuid, payload in list(payloadsByVortexUuid.items()):
            payload.filt = clientBranchIndexWatchUpdateFromDeviceFilt

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

        updateDatesTuples: BranchIndexUpdateDateTuple = payload.tuples[0]

        self._uuidsObserving.add(vortexUuid)

        yield self._replyToObserve(payload.filt,
                                   updateDatesTuples.updateDateByChunkKey,
                                   sendResponse,
                                   vortexUuid)

    # ---------------
    # Reply to device observe

    @inlineCallbacks
    def _replyToObserve(self, filt,
                        lastUpdateByBranchIndexKey: Dict[str, str],
                        sendResponse: SendVortexMsgResponseCallable,
                        vortexUuid: str) -> None:
        """ Reply to Observe

        The client has told us that it's observing a new set of branchIndexs, and the lastUpdate
        it has for each of those branchIndexs. We will send them the branchIndexs that are out of date
        or missing.

        :param filt: The payload filter to respond to.
        :param lastUpdateByBranchIndexKey: The dict of branchIndexKey:lastUpdate
        :param sendResponse: The callable provided by the Vortex (handy)
        :returns: None

        """
        yield None

        branchIndexTuplesToSend = []

        # Check and send any updates
        for branchIndexKey, lastUpdate in lastUpdateByBranchIndexKey.items():
            if vortexUuid not in VortexFactory.getRemoteVortexUuids():
                logger.debug("Vortex %s is offline, stopping update")
                return

            # NOTE: lastUpdate can be null.
            encodedBranchIndexTuple = self._cacheController.branchIndexChunk(branchIndexKey)
            if not encodedBranchIndexTuple:
                logger.debug("BranchIndex %s is not in the cache" % branchIndexKey)
                continue

            # We are king, If it's it's not our version, it's the wrong version ;-)
            logger.debug("%s, %s,  %s",
                         encodedBranchIndexTuple.lastUpdate == lastUpdate,
                         encodedBranchIndexTuple.lastUpdate, lastUpdate)

            if encodedBranchIndexTuple.lastUpdate == lastUpdate:
                logger.debug("BranchIndex %s matches the cache" % branchIndexKey)
                continue

            branchIndexTuplesToSend.append(encodedBranchIndexTuple)
            logger.debug("Sending branchIndex %s from the cache" % branchIndexKey)

        # Send the payload to the frontend
        payload = Payload(filt=filt, tuples=branchIndexTuplesToSend)
        d: Deferred = payload.makePayloadEnvelopeDefer()
        d.addCallback(lambda payloadEnvelope: payloadEnvelope.toVortexMsgDefer())
        d.addCallback(sendResponse)
        d.addErrback(vortexLogFailure, logger, consumeError=True)
