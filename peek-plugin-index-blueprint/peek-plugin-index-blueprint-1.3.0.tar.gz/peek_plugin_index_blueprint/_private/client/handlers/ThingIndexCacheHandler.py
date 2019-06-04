import logging
from collections import defaultdict
from typing import List, Dict

from twisted.internet.defer import DeferredList, inlineCallbacks, Deferred

from peek_plugin_index_blueprint._private.PluginNames import indexBlueprintFilt
from peek_plugin_index_blueprint._private.client.controller.ThingIndexCacheController import \
    ThingIndexCacheController
from peek_plugin_index_blueprint._private.tuples.ThingIndexUpdateDateTuple import \
    ThingIndexUpdateDateTuple
from vortex.DeferUtil import vortexLogFailure
from vortex.Payload import Payload
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.PayloadEnvelope import PayloadEnvelope
from vortex.VortexABC import SendVortexMsgResponseCallable
from vortex.VortexFactory import VortexFactory

logger = logging.getLogger(__name__)

clientThingIndexWatchUpdateFromDeviceFilt = {
    'key': "clientThingIndexWatchUpdateFromDevice"
}
clientThingIndexWatchUpdateFromDeviceFilt.update(indexBlueprintFilt)


# ModelSet HANDLER
class ThingIndexCacheHandler(object):
    def __init__(self, cacheController: ThingIndexCacheController,
                 clientId: str):
        """ App ThingIndex Handler

        This class handles the custom needs of the desktop/mobile apps observing thingIndexs.

        """
        self._cacheController = cacheController
        self._clientId = clientId

        self._epObserve = PayloadEndpoint(
            clientThingIndexWatchUpdateFromDeviceFilt, self._processObserve
        )

        self._uuidsObserving = set()

    def shutdown(self):
        self._epObserve.shutdown()
        self._epObserve = None

    # ---------------
    # Process update from the server

    def notifyOfThingIndexUpdate(self, chunkKeys: List[str]):
        """ Notify of ThingIndex Updates

        This method is called by the client.ThingIndexCacheController when it receives updates
        from the server.

        """
        vortexUuids = set(VortexFactory.getRemoteVortexUuids()) & self._uuidsObserving
        self._uuidsObserving = vortexUuids

        payloadsByVortexUuid = defaultdict(Payload)

        for chunkKey in chunkKeys:
            encodedThingIndexChunk = self._cacheController.thingIndexChunk(chunkKey)

            # Queue up the required client notifications
            for vortexUuid in vortexUuids:
                logger.debug("Sending unsolicited thingIndex %s to vortex %s",
                             chunkKey, vortexUuid)
                payloadsByVortexUuid[vortexUuid].tuples.append(encodedThingIndexChunk)

        # Send the updates to the clients
        dl = []
        for vortexUuid, payload in list(payloadsByVortexUuid.items()):
            payload.filt = clientThingIndexWatchUpdateFromDeviceFilt

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

        updateDatesTuples: ThingIndexUpdateDateTuple = payload.tuples[0]

        self._uuidsObserving.add(vortexUuid)

        yield self._replyToObserve(payload.filt,
                                   updateDatesTuples.updateDateByChunkKey,
                                   sendResponse,
                                   vortexUuid)

    # ---------------
    # Reply to device observe

    @inlineCallbacks
    def _replyToObserve(self, filt,
                        lastUpdateByThingIndexKey: Dict[str, str],
                        sendResponse: SendVortexMsgResponseCallable,
                        vortexUuid: str) -> None:
        """ Reply to Observe

        The client has told us that it's observing a new set of thingIndexs, and the lastUpdate
        it has for each of those thingIndexs. We will send them the thingIndexs that are out of date
        or missing.

        :param filt: The payload filter to respond to.
        :param lastUpdateByThingIndexKey: The dict of thingIndexKey:lastUpdate
        :param sendResponse: The callable provided by the Vortex (handy)
        :returns: None

        """
        yield None

        thingIndexTuplesToSend = []

        # Check and send any updates
        for thingIndexKey, lastUpdate in lastUpdateByThingIndexKey.items():
            if vortexUuid not in VortexFactory.getRemoteVortexUuids():
                logger.debug("Vortex %s is offline, stopping update")
                return

            # NOTE: lastUpdate can be null.
            encodedThingIndexTuple = self._cacheController.thingIndexChunk(thingIndexKey)
            if not encodedThingIndexTuple:
                logger.debug("ThingIndex %s is not in the cache" % thingIndexKey)
                continue

            # We are king, If it's it's not our version, it's the wrong version ;-)
            logger.debug("%s, %s,  %s",
                         encodedThingIndexTuple.lastUpdate == lastUpdate,
                         encodedThingIndexTuple.lastUpdate, lastUpdate)

            if encodedThingIndexTuple.lastUpdate == lastUpdate:
                logger.debug("ThingIndex %s matches the cache" % thingIndexKey)
                continue

            thingIndexTuplesToSend.append(encodedThingIndexTuple)
            logger.debug("Sending thingIndex %s from the cache" % thingIndexKey)

        # Send the payload to the frontend
        payload = Payload(filt=filt, tuples=thingIndexTuplesToSend)
        d: Deferred = payload.makePayloadEnvelopeDefer()
        d.addCallback(lambda payloadEnvelope: payloadEnvelope.toVortexMsgDefer())
        d.addCallback(sendResponse)
        d.addErrback(vortexLogFailure, logger, consumeError=True)
