import logging
from typing import List, Optional

from twisted.internet.defer import Deferred

from peek_plugin_base.PeekVortexUtil import peekClientName
from peek_plugin_base.storage.StorageUtil import makeOrmValuesSubqueryCondition
from peek_plugin_diagram._private.client.controller.GridCacheController import \
    clientGridUpdateFromServerFilt
from peek_plugin_diagram._private.storage.GridKeyIndex import GridKeyIndexCompiled
from peek_plugin_diagram._private.tuples.grid.GridTuple import GridTuple
from peek_plugin_diagram._private.tuples.grid.EncodedGridTuple import EncodedGridTuple
from vortex.DeferUtil import vortexLogFailure, deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.VortexFactory import VortexFactory, NoVortexException

logger = logging.getLogger(__name__)


class ClientGridUpdateHandler:
    """ Client Update Controller

    This controller handles sending updates the the client.

    It uses lower level Vortex API

    It does the following a broadcast to all clients:

    1) Sends grid updates to the clients

    2) Sends Lookup updates to the clients

    """

    def __init__(self, dbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

    def shutdown(self):
        pass

    def sendGrids(self, gridKeys: List[str]) -> None:
        """ Send Grids

        Send grid updates to the client services

        :param gridKeys: A list of grid keys that this client is observing.
                            the grids are sent to the requesting client only.
        :returns: Nothing
        """

        if not gridKeys:
            return

        if peekClientName not in VortexFactory.getRemoteVortexName():
            logger.debug("No clients are online to send the grid to, %s", gridKeys)
            return

        def send(vortexMsg: Optional[bytes]):
            if vortexMsg:
                VortexFactory.sendVortexMsg(
                    vortexMsg, destVortexName=peekClientName
                )

        d: Deferred = self._serialiseGrids(gridKeys)
        d.addCallback(send)
        d.addErrback(self._sendGridsErrback, gridKeys)

    def _sendGridsErrback(self, failure, gridKeys):

        if failure.check(NoVortexException):
            logger.debug(
                "No clients are online to send the grid to, %s", gridKeys)
            return

        vortexLogFailure(failure, logger)

    @deferToThreadWrapWithLogger(logger)
    def _serialiseGrids(self, gridKeys) -> Optional[bytes]:
        session = self._dbSessionCreator()
        try:
            ormGrids = (session.query(GridKeyIndexCompiled)
                        .filter(makeOrmValuesSubqueryCondition(
                            session, GridKeyIndexCompiled.gridKey, gridKeys
                        ))
                        .yield_per(200))

            gridTuples: List[EncodedGridTuple] = []
            for ormGrid in ormGrids:
                gridTuples.append(
                    EncodedGridTuple(gridKey=ormGrid.gridKey,
                                     encodedGridTuple=ormGrid.encodedGridTuple,
                                     lastUpdate=ormGrid.lastUpdate)
                )

            if not gridTuples:
                return None

            return Payload(
                filt=clientGridUpdateFromServerFilt, tuples=gridTuples
                           ).makePayloadEnvelope().toVortexMsg()

        finally:
            session.close()
