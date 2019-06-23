import logging
from typing import List

from peek_plugin_base.PeekVortexUtil import peekServerName, peekClientName
from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_plugin_graphdb._private.PluginNames import graphDbFilt
from peek_plugin_graphdb._private.storage.GraphDbEncodedChunk import GraphDbEncodedChunk
from vortex.rpc.RPC import vortexRPC

from peek_plugin_graphdb._private.tuples.GraphDbEncodedChunkTuple import \
    GraphDbEncodedChunkTuple

logger = logging.getLogger(__name__)


class SegmentIndexChunkLoadRpc:
    def __init__(self, dbSessionCreator: DbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

    def makeHandlers(self):
        """ Make Handlers

        In this method we start all the RPC handlers
        start() returns an instance of it's self so we can simply yield the result
        of the start method.

        """

        yield self.loadSegmentChunks.start(funcSelf=self)
        logger.debug("RPCs started")

    # -------------
    @vortexRPC(peekServerName, acceptOnlyFromVortex=peekClientName, timeoutSeconds=60,
               additionalFilt=graphDbFilt, deferToThread=True)
    def loadSegmentChunks(self, offset: int, count: int) -> List[GraphDbEncodedChunkTuple]:
        """ Load Segment Chunks

        Allow the client to incrementally load the chunks.

        """
        session = self._dbSessionCreator()
        try:
            chunks = (session
                      .query(GraphDbEncodedChunk)
                      .order_by(GraphDbEncodedChunk.id)
                      .offset(offset)
                      .limit(count)
                      .yield_per(count))

            return [o.toTuple() for o in chunks]

        finally:
            session.close()
