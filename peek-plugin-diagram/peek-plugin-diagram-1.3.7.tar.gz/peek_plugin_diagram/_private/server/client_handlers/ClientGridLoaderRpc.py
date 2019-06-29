import logging
from typing import List

from peek_plugin_base.PeekVortexUtil import peekServerName, peekClientName
from peek_plugin_diagram._private.PluginNames import diagramFilt
from peek_plugin_diagram._private.storage.GridKeyIndex import GridKeyIndexCompiled
from peek_plugin_diagram._private.tuples.grid.EncodedGridTuple import EncodedGridTuple
from peek_plugin_diagram._private.tuples.grid.GridTuple import GridTuple
from vortex.DeferUtil import vortexLogFailure
from vortex.rpc.RPC import vortexRPC

logger = logging.getLogger(__name__)


class ClientGridLoaderRpc:
    def __init__(self, liveDbWatchController, dbSessionCreator):
        self._liveDbWatchController = liveDbWatchController
        self._dbSessionCreator = dbSessionCreator

    def makeHandlers(self):
        """ Make Handlers

        In this method we start all the RPC handlers
        start() returns an instance of it's self so we can simply yield the result
        of the start method.

        """

        yield self.loadGrids.start(funcSelf=self)
        yield self.updateClientWatchedGrids.start(funcSelf=self)
        logger.debug("RPCs started")

    # -------------
    @vortexRPC(peekServerName, acceptOnlyFromVortex=peekClientName,timeoutSeconds=120,
               additionalFilt=diagramFilt, deferToThread=True)
    def loadGrids(self, offset: int, count: int) -> List[GridTuple]:
        """ Update Page Loader Status

        Tell the server of the latest status of the loader

        """
        session = self._dbSessionCreator()
        try:
            ormGrids = (session
                        .query(GridKeyIndexCompiled)
                        .order_by(GridKeyIndexCompiled.id)
                        .offset(offset)
                        .limit(count)
                        .yield_per(200))

            gridTuples: List[GridTuple] = []
            for ormGrid in ormGrids:
                gridTuples.append(
                    EncodedGridTuple(gridKey=ormGrid.gridKey,
                              encodedGridTuple=ormGrid.encodedGridTuple,
                              lastUpdate=ormGrid.lastUpdate)
                )

            return gridTuples

        finally:
            session.close()



    # -------------
    @vortexRPC(peekServerName, acceptOnlyFromVortex=peekClientName,
               additionalFilt=diagramFilt)
    def updateClientWatchedGrids(self, clientId: str, gridKeys: List[str]) -> None:
        """ Update Client Watched Grids

        Tell the server that these grids are currently being watched by users.

        :param clientId: A unique identifier of the client (Maybe it's vortex uuid)
        :param gridKeys: A list of grid keys that this client is observing.
        :returns: Nothing
        """

        d = self._liveDbWatchController.updateClientWatchedGrids(clientId, gridKeys)
        d.addErrback(vortexLogFailure, logger, consumeError=True)
