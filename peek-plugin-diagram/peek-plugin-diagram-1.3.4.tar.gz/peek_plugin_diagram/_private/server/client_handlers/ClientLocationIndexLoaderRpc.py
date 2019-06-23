import logging
from typing import List

from peek_plugin_base.PeekVortexUtil import peekServerName, peekClientName
from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_plugin_diagram._private.PluginNames import diagramFilt
from peek_plugin_diagram._private.storage.LocationIndex import LocationIndexCompiled
from peek_plugin_diagram._private.storage.ModelSet import ModelSet
from peek_plugin_diagram._private.tuples.location_index.EncodedLocationIndexTuple import \
    EncodedLocationIndexTuple
from peek_plugin_diagram._private.tuples.location_index.LocationIndexTuple import LocationIndexTuple
from vortex.rpc.RPC import vortexRPC

logger = logging.getLogger(__name__)


class ClientLocationIndexLoaderRpc:
    def __init__(self, dbSessionCreator: DbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

    def makeHandlers(self):
        """ Make Handlers

        In this method we start all the RPC handlers
        start() returns an instance of it's self so we can simply yield the result
        of the start method.

        """

        yield self.loadLocationIndexes.start(funcSelf=self)
        logger.debug("RPCs started")

    # -------------
    @vortexRPC(peekServerName, acceptOnlyFromVortex=peekClientName, timeoutSeconds=60,
               additionalFilt=diagramFilt, deferToThread=True)
    def loadLocationIndexes(self, offset: int, count: int) -> List[EncodedLocationIndexTuple]:
        """ Update Page Loader Status

        Tell the server of the latest status of the loader

        """
        session = self._dbSessionCreator()
        try:
            ormLocationIndexes = (session
                .query(LocationIndexCompiled.indexBucket,
                       LocationIndexCompiled.blobData,
                       LocationIndexCompiled.lastUpdate,
                       ModelSet.key)
                .join(ModelSet)
                .order_by(LocationIndexCompiled.id)
                .offset(offset)
                .limit(count)
                .yield_per(200))

            gridTuples: List[LocationIndexTuple] = []
            for obj in ormLocationIndexes:
                gridTuples.append(
                    EncodedLocationIndexTuple(indexBucket=obj.indexBucket,
                                              encodedLocationIndexTuple=obj.blobData,
                                              lastUpdate=obj.lastUpdate,
                                              modelSetKey=obj.key)
                )

            return gridTuples

        finally:
            session.close()
