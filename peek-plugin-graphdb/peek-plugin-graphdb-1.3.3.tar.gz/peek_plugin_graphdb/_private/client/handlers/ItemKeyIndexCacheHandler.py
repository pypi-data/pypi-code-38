import logging
from collections import defaultdict
from typing import List, Dict

from twisted.internet.defer import DeferredList, inlineCallbacks, Deferred

from peek_plugin_graphdb._private.PluginNames import graphDbFilt
from peek_plugin_graphdb._private.client.controller.ItemKeyIndexCacheController import \
    ItemKeyIndexCacheController
from peek_plugin_graphdb._private.tuples.ItemKeyIndexUpdateDateTuple import \
    ItemKeyIndexUpdateDateTuple
from vortex.DeferUtil import vortexLogFailure
from vortex.Payload import Payload
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.PayloadEnvelope import PayloadEnvelope
from vortex.VortexABC import SendVortexMsgResponseCallable
from vortex.VortexFactory import VortexFactory

logger = logging.getLogger(__name__)

clientItemKeyIndexWatchUpdateFromDeviceFilt = {
    'key': "clientItemKeyIndexWatchUpdateFromDevice"
}
clientItemKeyIndexWatchUpdateFromDeviceFilt.update(graphDbFilt)


# ModelSet HANDLER
class ItemKeyIndexCacheHandler(object):
    def __init__(self, cacheController: ItemKeyIndexCacheController,
                 clientId: str):
        """ App ItemKeyIndex Handler

        This class handles the custom needs of the desktop/mobile apps observing itemKeyIndexs.

        """
        self._cacheController = cacheController
        self._clientId = clientId

        self._epObserve = PayloadEndpoint(
            clientItemKeyIndexWatchUpdateFromDeviceFilt, self._processObserve
        )

        self._uuidsObserving = set()

    def shutdown(self):
        self._epObserve.shutdown()
        self._epObserve = None

    # ---------------
    # Process update from the server

    def notifyOfItemKeyIndexUpdate(self, chunkKeys: List[str]):
        """ Notify of ItemKeyIndex Updates

        This method is called by the client.ItemKeyIndexCacheController when it receives updates
        from the server.

        """
        vortexUuids = set(VortexFactory.getRemoteVortexUuids()) & self._uuidsObserving
        self._uuidsObserving = vortexUuids

        payloadsByVortexUuid = defaultdict(Payload)

        for chunkKey in chunkKeys:
            encodedItemKeyIndexChunk = self._cacheController.itemKeyIndexChunk(chunkKey)

            # Queue up the required client notifications
            for vortexUuid in vortexUuids:
                logger.debug("Sending unsolicited itemKeyIndex %s to vortex %s",
                             chunkKey, vortexUuid)
                payloadsByVortexUuid[vortexUuid].tuples.append(encodedItemKeyIndexChunk)

        # Send the updates to the clients
        dl = []
        for vortexUuid, payload in list(payloadsByVortexUuid.items()):
            payload.filt = clientItemKeyIndexWatchUpdateFromDeviceFilt

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

        updateDatesTuples: ItemKeyIndexUpdateDateTuple = payload.tuples[0]

        self._uuidsObserving.add(vortexUuid)

        yield self._replyToObserve(payload.filt,
                                   updateDatesTuples.updateDateByChunkKey,
                                   sendResponse,
                                   vortexUuid)

    # ---------------
    # Reply to device observe

    @inlineCallbacks
    def _replyToObserve(self, filt,
                        lastUpdateByItemKeyIndexKey: Dict[str, str],
                        sendResponse: SendVortexMsgResponseCallable,
                        vortexUuid: str) -> None:
        """ Reply to Observe

        The client has told us that it's observing a new set of itemKeyIndexs, and the lastUpdate
        it has for each of those itemKeyIndexs. We will send them the itemKeyIndexs that are out of date
        or missing.

        :param filt: The payload filter to respond to.
        :param lastUpdateByItemKeyIndexKey: The dict of itemKeyIndexKey:lastUpdate
        :param sendResponse: The callable provided by the Vortex (handy)
        :returns: None

        """
        yield None

        itemKeyIndexTuplesToSend = []

        # Check and send any updates
        for itemKeyIndexKey, lastUpdate in lastUpdateByItemKeyIndexKey.items():
            if vortexUuid not in VortexFactory.getRemoteVortexUuids():
                logger.debug("Vortex %s is offline, stopping update")
                return

            # NOTE: lastUpdate can be null.
            encodedItemKeyIndexTuple = self._cacheController.itemKeyIndexChunk(itemKeyIndexKey)
            if not encodedItemKeyIndexTuple:
                logger.debug("ItemKeyIndex %s is not in the cache" % itemKeyIndexKey)
                continue

            # We are king, If it's it's not our version, it's the wrong version ;-)
            logger.debug("%s, %s,  %s",
                         encodedItemKeyIndexTuple.lastUpdate == lastUpdate,
                         encodedItemKeyIndexTuple.lastUpdate, lastUpdate)

            if encodedItemKeyIndexTuple.lastUpdate == lastUpdate:
                logger.debug("ItemKeyIndex %s matches the cache" % itemKeyIndexKey)
                continue

            itemKeyIndexTuplesToSend.append(encodedItemKeyIndexTuple)
            logger.debug("Sending itemKeyIndex %s from the cache" % itemKeyIndexKey)

        # Send the payload to the frontend
        payload = Payload(filt=filt, tuples=itemKeyIndexTuplesToSend)
        d: Deferred = payload.makePayloadEnvelopeDefer()
        d.addCallback(lambda payloadEnvelope: payloadEnvelope.toVortexMsgDefer())
        d.addCallback(sendResponse)
        d.addErrback(vortexLogFailure, logger, consumeError=True)
