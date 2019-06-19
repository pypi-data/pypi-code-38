import logging
from collections import defaultdict
from typing import List, Dict

from twisted.internet.defer import DeferredList, inlineCallbacks, Deferred

from peek_core_search._private.PluginNames import searchFilt
from peek_core_search._private.client.controller.SearchObjectCacheController import \
    SearchObjectCacheController
from peek_core_search._private.tuples.search_object.SearchObjectUpdateDateTuple import \
    SearchObjectUpdateDateTuple
from vortex.DeferUtil import vortexLogFailure
from vortex.Payload import Payload
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.PayloadEnvelope import PayloadEnvelope
from vortex.VortexABC import SendVortexMsgResponseCallable
from vortex.VortexFactory import VortexFactory

logger = logging.getLogger(__name__)

clientSearchObjectWatchUpdateFromDeviceFilt = {
    'key': "clientSearchObjectWatchUpdateFromDevice"
}
clientSearchObjectWatchUpdateFromDeviceFilt.update(searchFilt)


# ModelSet HANDLER
class SearchObjectCacheHandler(object):
    def __init__(self, cacheController: SearchObjectCacheController,
                 clientId: str):
        """ App SearchObject Handler

        This class handles the custom needs of the desktop/mobile apps observing searchObjects.

        """
        self._cacheController = cacheController
        self._clientId = clientId

        self._epObserve = PayloadEndpoint(
            clientSearchObjectWatchUpdateFromDeviceFilt, self._processObserve
        )

        self._uuidsObserving = set()

    def shutdown(self):
        self._epObserve.shutdown()
        self._epObserve = None

    # ---------------
    # Process update from the server

    def notifyOfSearchObjectUpdate(self, chunkKeys: List[str]):
        """ Notify of SearchObject Updates

        This method is called by the client.SearchObjectCacheController when it receives updates
        from the server.

        """
        vortexUuids = set(VortexFactory.getRemoteVortexUuids()) & self._uuidsObserving
        self._uuidsObserving = vortexUuids

        payloadsByVortexUuid = defaultdict(Payload)

        for chunkKey in chunkKeys:
            encodedSearchObjectChunk = self._cacheController.searchObject(chunkKey)

            # Queue up the required client notifications
            for vortexUuid in vortexUuids:
                logger.debug("Sending unsolicited searchObject %s to vortex %s",
                             chunkKey, vortexUuid)
                payloadsByVortexUuid[vortexUuid].tuples.append(encodedSearchObjectChunk)

        # Send the updates to the clients
        dl = []
        for vortexUuid, payload in list(payloadsByVortexUuid.items()):
            payload.filt = clientSearchObjectWatchUpdateFromDeviceFilt

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

        updateDatesTuples: SearchObjectUpdateDateTuple = payload.tuples[0]

        self._uuidsObserving.add(vortexUuid)

        yield self._replyToObserve(payload.filt,
                                   updateDatesTuples.updateDateByChunkKey,
                                   sendResponse,
                                   vortexUuid)

    # ---------------
    # Reply to device observe

    @inlineCallbacks
    def _replyToObserve(self, filt,
                        lastUpdateBySearchObjectKey: Dict[str, str],
                        sendResponse: SendVortexMsgResponseCallable,
                        vortexUuid: str) -> None:
        """ Reply to Observe

        The client has told us that it's observing a new set of searchObjects, and the lastUpdate
        it has for each of those searchObjects. We will send them the searchObjects that are out of date
        or missing.

        :param filt: The payload filter to respond to.
        :param lastUpdateBySearchObjectKey: The dict of searchObjectKey:lastUpdate
        :param sendResponse: The callable provided by the Vortex (handy)
        :returns: None

        """
        yield None

        searchObjectTuplesToSend = []

        # Check and send any updates
        for searchObjectKey, lastUpdate in lastUpdateBySearchObjectKey.items():
            if vortexUuid not in VortexFactory.getRemoteVortexUuids():
                logger.debug("Vortex %s is offline, stopping update")
                return

            searchObjectKey = int(searchObjectKey)

            # NOTE: lastUpdate can be null.
            encodedSearchObjectTuple = self._cacheController.searchObject(searchObjectKey)
            if not encodedSearchObjectTuple:
                logger.debug("SearchObject %s is not in the cache" % searchObjectKey)
                continue

            # We are king, If it's it's not our version, it's the wrong version ;-)
            logger.debug("%s, %s,  %s",
                         encodedSearchObjectTuple.lastUpdate == lastUpdate,
                         encodedSearchObjectTuple.lastUpdate, lastUpdate)

            if encodedSearchObjectTuple.lastUpdate == lastUpdate:
                logger.debug("SearchObject %s matches the cache" % searchObjectKey)
                continue

            searchObjectTuplesToSend.append(encodedSearchObjectTuple)
            logger.debug("Sending searchObject %s from the cache" % searchObjectKey)

        # Send the payload to the frontend
        payload = Payload(filt=filt, tuples=searchObjectTuplesToSend)
        d: Deferred = payload.makePayloadEnvelopeDefer()
        d.addCallback(lambda payloadEnvelope: payloadEnvelope.toVortexMsgDefer())
        d.addCallback(sendResponse)
        d.addErrback(vortexLogFailure, logger, consumeError=True)
