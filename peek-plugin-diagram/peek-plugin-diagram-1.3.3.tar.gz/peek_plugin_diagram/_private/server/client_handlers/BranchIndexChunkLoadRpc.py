import logging
from typing import List

from peek_plugin_base.PeekVortexUtil import peekServerName, peekClientName
from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_plugin_diagram._private.PluginNames import diagramFilt
from peek_plugin_diagram._private.storage.branch.BranchIndexEncodedChunk import BranchIndexEncodedChunk
from vortex.rpc.RPC import vortexRPC

logger = logging.getLogger(__name__)


class BranchIndexChunkLoadRpc:
    def __init__(self, dbSessionCreator: DbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

    def makeHandlers(self):
        """ Make Handlers

        In this method we start all the RPC handlers
        start() returns an instance of it's self so we can simply yield the result
        of the start method.

        """

        yield self.loadBranchIndexChunks.start(funcSelf=self)
        logger.debug("RPCs started")

    # -------------
    @vortexRPC(peekServerName, acceptOnlyFromVortex=peekClientName, timeoutSeconds=60,
               additionalFilt=diagramFilt, deferToThread=True)
    def loadBranchIndexChunks(self, offset: int, count: int) -> List[BranchIndexEncodedChunk]:
        """ Update Page Loader Status

        Tell the server of the latest status of the loader

        """
        session = self._dbSessionCreator()
        try:
            chunks = (session
                      .query(BranchIndexEncodedChunk)
                      .order_by(BranchIndexEncodedChunk.id)
                      .offset(offset)
                      .limit(count)
                      .yield_per(count))

            return list(chunks)

        finally:
            session.close()
