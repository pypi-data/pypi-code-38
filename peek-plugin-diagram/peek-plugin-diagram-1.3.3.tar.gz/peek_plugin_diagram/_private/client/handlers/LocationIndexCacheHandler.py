import logging
from collections import defaultdict
from typing import List

from twisted.internet.defer import DeferredList, inlineCallbacks, Deferred

from peek_plugin_diagram._private.PluginNames import diagramFilt
from peek_plugin_diagram._private.client.controller.LocationIndexCacheController import \
    LocationIndexCacheController
from peek_plugin_diagram._private.tuples.location_index.LocationIndexUpdateDateTuple import \
    LocationIndexUpdateDateTuple, DeviceLocationIndexT
from vortex.DeferUtil import vortexLogFailure
from vortex.Payload import Payload
from vortex.PayloadEndpoint import PayloadEndpoint
from vortex.PayloadEnvelope import PayloadEnvelope
from vortex.VortexABC import SendVortexMsgResponseCallable
from vortex.VortexFactory import VortexFactory

logger = logging.getLogger(__name__)

clientLocationIndexWatchUpdateFromDeviceFilt = {
    'key': "clientLocationIndexWatchUpdateFromDevice"
}
clientLocationIndexWatchUpdateFromDeviceFilt.update(diagramFilt)


# ModelSet HANDLER
class LocationIndexCacheHandler(object):
    def __init__(self, locationIndexCacheController: LocationIndexCacheController,
                 clientId: str):
        """ App LocationIndexCacheHandler Handler

        This class handles the custom needs of the desktop/mobile apps observing locationIndexs.

        """
        self._cacheController = locationIndexCacheController
        self._clientId = clientId

        self._epObserve = PayloadEndpoint(
            clientLocationIndexWatchUpdateFromDeviceFilt, self._processObserve
        )

        self._observingVortexUuid = set()

    def shutdown(self):
        self._epObserve.shutdown()
        self._epObserve = None

    # ---------------
    # Process update from the server

    def notifyOfLocationIndexUpdate(self, locationIndexKeys: List[str]):
        """ Notify of LocationIndexCacheHandler Updates

        This method is called by the client.LocationIndexCacheController when it receives updates
        from the server.

        """
        self._observingVortexUuid = (
                self._observingVortexUuid & set(VortexFactory.getRemoteVortexUuids())
        )

        payloadsByVortexUuid = defaultdict(Payload)

        for locationIndexKey in locationIndexKeys:

            locationIndexTuple = self._cacheController.locationIndex(locationIndexKey)

            # Queue up the required client notifications
            for vortexUuid in self._observingVortexUuid:
                logger.debug("Sending unsolicited locationIndex %s to vortex %s",
                             locationIndexKey, vortexUuid)
                payloadsByVortexUuid[vortexUuid].tuples.append(locationIndexTuple)

        # Send the updates to the clients
        dl = []
        for vortexUuid, payload in list(payloadsByVortexUuid.items()):
            payload.filt = clientLocationIndexWatchUpdateFromDeviceFilt

            # Serliase in thread, and then send.
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

        updateDatesTuples: LocationIndexUpdateDateTuple = payload.tuples[0]

        self._observingVortexUuid.add(vortexUuid)

        yield self._replyToObserve(payload.filt,
                                   updateDatesTuples.updateDateByChunkKey,
                                   sendResponse,
                                   vortexUuid)

    # ---------------
    # Reply to device observe

    @inlineCallbacks
    def _replyToObserve(self, filt,
                        lastUpdateByLocationIndexKey: DeviceLocationIndexT,
                        sendResponse: SendVortexMsgResponseCallable,
                        vortexUuid: str) -> None:
        """ Reply to Observe

        The client has told us that it's observing a new set of locationIndexs, and the lastUpdate
        it has for each of those locationIndexs. We will send them the locationIndexs that are out of date
        or missing.

        :param filt: The payload filter to respond to.
        :param lastUpdateByLocationIndexKey: The dict of locationIndexKey:lastUpdate
        :param sendResponse: The callable provided by the Vortex (handy)
        :returns: None

        """
        yield None

        locationIndexTuplesToSend = []

        # Check and send any updates
        for locationIndexKey, lastUpdate in lastUpdateByLocationIndexKey.items():
            if vortexUuid not in VortexFactory.getRemoteVortexUuids():
                logger.debug("Vortex %s is offline, stopping update")
                return

            # NOTE: lastUpdate can be null.
            encodedLocationIndexTuple = self._cacheController.locationIndex(
                locationIndexKey)
            if not encodedLocationIndexTuple:
                logger.debug(
                    "LocationIndexCacheHandler %s is not in the cache" % locationIndexKey)
                continue

            # We are king, If it's it's not our version, it's the wrong version ;-)
            logger.debug("%s, %s,  %s",
                         encodedLocationIndexTuple.lastUpdate == lastUpdate,
                         encodedLocationIndexTuple.lastUpdate, lastUpdate)

            if encodedLocationIndexTuple.lastUpdate == lastUpdate:
                logger.debug(
                    "LocationIndexCacheHandler %s matches the cache" % locationIndexKey)
                continue

            locationIndexTuplesToSend.append(encodedLocationIndexTuple)
            logger.debug("Sending locationIndex %s from the cache" % locationIndexKey)

        # Send the payload to the frontend
        payload = Payload(filt=filt, tuples=locationIndexTuplesToSend)
        d: Deferred = payload.makePayloadEnvelopeDefer()
        d.addCallback(lambda payloadEnvelope: payloadEnvelope.toVortexMsgDefer())
        d.addCallback(sendResponse)
        d.addErrback(vortexLogFailure, logger, consumeError=True)
