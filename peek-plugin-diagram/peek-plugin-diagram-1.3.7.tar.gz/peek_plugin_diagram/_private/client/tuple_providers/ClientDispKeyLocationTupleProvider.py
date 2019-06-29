import ujson as json
import logging
from collections import defaultdict
from typing import Union, List

from twisted.internet.defer import Deferred

from peek_plugin_diagram._private.client.controller.CoordSetCacheController import \
    CoordSetCacheController
from peek_plugin_diagram._private.client.controller.LocationIndexCacheController import \
    LocationIndexCacheController
from peek_plugin_diagram._private.storage.LocationIndex import LocationIndexCompiled
from peek_plugin_diagram._private.tuples.location_index.DispKeyLocationTuple import \
    DispKeyLocationTuple
from peek_plugin_diagram._private.tuples.location_index.EncodedLocationIndexTuple import \
    EncodedLocationIndexTuple
from peek_plugin_diagram._private.tuples.location_index.LocationIndexTuple import \
    LocationIndexTuple
from peek_plugin_diagram._private.worker.tasks._CalcLocation import dispKeyHashBucket
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)


class ClientDispKeyLocationTupleProvider(TuplesProviderABC):
    """ Client Location Index Tuple Provider

    This class is used by the UIs when they have the offline location index
    switched off.
    
    """

    def __init__(self, locationCache: LocationIndexCacheController,
                 coordSetCache: CoordSetCacheController):
        self._locationCache = locationCache
        self._coordSetCache = coordSetCache

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict,
                      tupleSelector: TupleSelector) -> Union[Deferred, bytes]:
        modelSetKey = tupleSelector.selector["modelSetKey"]
        keys = tupleSelector.selector["keys"]

        keysByChunkKey = defaultdict(list)

        foundLocationIndexes: List[LocationIndexTuple] = []

        for key in keys:
            keysByChunkKey[dispKeyHashBucket(modelSetKey, key)].append(key)

        for chunkKey, subKeys in keysByChunkKey.items():
            chunk: EncodedLocationIndexTuple = self._locationCache.locationIndex(chunkKey)

            if not chunk:
                logger.warning("Location index chunk %s is missing from cache", chunkKey)
                continue

            jsonStr = Payload().fromEncodedPayload(chunk.encodedLocationIndexTuple).tuples[0].jsonStr
            locationsByKey = {i[0]: i[1:] for i in json.loads(jsonStr)}

            for subKey in subKeys:
                if subKey not in locationsByKey:
                    logger.warning(
                        "LocationIndex %s is missing from index, chunkKey %s",
                        subKey, chunkKey
                    )
                    continue

                # Reconstruct the data
                for locationJsonStr in locationsByKey[subKey]:
                    dispLocation = DispKeyLocationTuple.fromLocationJson(locationJsonStr)
                    foundLocationIndexes.append(dispLocation)

                    # Populate the coord set key
                    coordSet = self._coordSetCache.coordSetForId(dispLocation.coordSetId)

                    if coordSet is None:
                        logger.warning("Can not find coordSet with ID %s",
                                       dispLocation.coordSetId)
                        continue

                    dispLocation.coordSetKey = coordSet.key

        # Create the vortex message
        return Payload(filt,
                       tuples=foundLocationIndexes).makePayloadEnvelope().toVortexMsg()
