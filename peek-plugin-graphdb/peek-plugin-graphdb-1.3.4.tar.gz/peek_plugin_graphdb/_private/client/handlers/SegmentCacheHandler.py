import logging
from collections import defaultdict
from typing import List, Dict

from twisted.internet.defer import DeferredList, inlineCallbacks, Deferred

from peek_plugin_graphdb._private.PluginNames import graphDbFilt
from peek_plugin_graphdb._private.client.controller.SegmentCacheController import \
    SegmentCacheController
from peek_plugin_graphdb._private.tuples.SegmentIndexUpdateDateTuple import \
    SegmentIndexUpdateDateTuple
from vortex.DeferUtil import vortexLogFailure
from vortex.Payload import Payload
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.PayloadEnvelope import PayloadEnvelope
from vortex.VortexABC import SendVortexMsgResponseCallable
from vortex.VortexFactory import VortexFactory

logger = logging.getLogger(__name__)

clientSegmentWatchUpdateFromDeviceFilt = {
    'key': "clientSegmentWatchUpdateFromDevice"
}
clientSegmentWatchUpdateFromDeviceFilt.update(graphDbFilt)


# ModelSet HANDLER
class SegmentCacheHandler(object):
    def __init__(self, cacheController: SegmentCacheController,
                 clientId: str):
        """ App Segment Handler

        This class handles the custom needs of the desktop/mobile apps observing segments.

        """
        self._cacheController = cacheController
        self._clientId = clientId

        self._epObserve = PayloadEndpoint(
            clientSegmentWatchUpdateFromDeviceFilt, self._processObserve
        )

        self._uuidsObserving = set()

    def shutdown(self):
        self._epObserve.shutdown()
        self._epObserve = None

    # ---------------
    # Process update from the server

    def notifyOfSegmentUpdate(self, chunkKeys: List[str]):
        """ Notify of Segment Updates

        This method is called by the client.SegmentCacheController when it receives updates
        from the server.

        """
        vortexUuids = set(VortexFactory.getRemoteVortexUuids()) & self._uuidsObserving
        self._uuidsObserving = vortexUuids

        payloadsByVortexUuid = defaultdict(Payload)

        for chunkKey in chunkKeys:
            encodedSegmentChunk = self._cacheController.segmentChunk(chunkKey)

            # Queue up the required client notifications
            for vortexUuid in vortexUuids:
                logger.debug("Sending unsolicited segment %s to vortex %s",
                             chunkKey, vortexUuid)
                payloadsByVortexUuid[vortexUuid].tuples.append(encodedSegmentChunk)

        # Send the updates to the clients
        dl = []
        for vortexUuid, payload in list(payloadsByVortexUuid.items()):
            payload.filt = clientSegmentWatchUpdateFromDeviceFilt

            # Serialise in thread, and then send.
            d = payload.makePayloadEnvelopeDefer()
            d.addCallback(lambda payloadEnvelope: payloadEnvelope.toVortexMsgDefer())
            d.addCallback(VortexFactory.sendVortexMsg, destVortexUuid=vortexUuid)
            dl.append(d)

        return DeferredList(dl, fireOnOneErrback=True)

    # ---------------
    # Process observes from the devices
    @inlineCallbacks
    def _processObserve(self, payloadEnvelope: PayloadEnvelope,
                        vortexUuid: str,
                        sendResponse: SendVortexMsgResponseCallable,
                        **kwargs):

        payload = yield payloadEnvelope.decodePayloadDefer()

        updateDatesTuples: SegmentIndexUpdateDateTuple = payload.tuples[0]

        self._uuidsObserving.add(vortexUuid)

        yield self._replyToObserve(payload.filt,
                                   updateDatesTuples.updateDateByChunkKey,
                                   sendResponse,
                                   vortexUuid)

    # ---------------
    # Reply to device observe

    @inlineCallbacks
    def _replyToObserve(self, filt,
                        lastUpdateBySegmentKey: Dict[str, str],
                        sendResponse: SendVortexMsgResponseCallable,
                        vortexUuid: str) -> None:
        """ Reply to Observe

        The client has told us that it's observing a new set of segments, and the lastUpdate
        it has for each of those segments. We will send them the segments that are out of date
        or missing.

        :param filt: The payload filter to respond to.
        :param lastUpdateBySegmentKey: The dict of segmentKey:lastUpdate
        :param sendResponse: The callable provided by the Vortex (handy)
        :returns: None

        """
        yield None

        segmentTuplesToSend = []

        # Check and send any updates
        for segmentKey, lastUpdate in lastUpdateBySegmentKey.items():
            if vortexUuid not in VortexFactory.getRemoteVortexUuids():
                logger.debug("Vortex %s is offline, stopping update")
                return

            # NOTE: lastUpdate can be null.
            encodedSegmentTuple = self._cacheController.segmentChunk(segmentKey)
            if not encodedSegmentTuple:
                logger.debug("Segment %s is not in the cache" % segmentKey)
                continue

            # We are king, If it's it's not our version, it's the wrong version ;-)
            logger.debug("%s, %s,  %s",
                         encodedSegmentTuple.lastUpdate == lastUpdate,
                         encodedSegmentTuple.lastUpdate, lastUpdate)

            if encodedSegmentTuple.lastUpdate == lastUpdate:
                logger.debug("Segment %s matches the cache" % segmentKey)
                continue

            segmentTuplesToSend.append(encodedSegmentTuple)
            logger.debug("Sending segment %s from the cache" % segmentKey)

        # Send the payload to the frontend
        payload = Payload(filt=filt, tuples=segmentTuplesToSend)
        d: Deferred = payload.makePayloadEnvelopeDefer()
        d.addCallback(lambda payloadEnvelope: payloadEnvelope.toVortexMsgDefer())
        d.addCallback(sendResponse)
        d.addErrback(vortexLogFailure, logger, consumeError=True)
