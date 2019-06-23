import logging
from typing import List

from peek_plugin_base.PeekVortexUtil import peekServerName, peekClientName
from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_core_search._private.PluginNames import searchFilt
from peek_core_search._private.storage.EncodedSearchIndexChunk import \
    EncodedSearchIndexChunk
from peek_core_search._private.storage.EncodedSearchObjectChunk import \
    EncodedSearchObjectChunk
from vortex.rpc.RPC import vortexRPC

logger = logging.getLogger(__name__)


class ClientChunkLoadRpc:
    def __init__(self, dbSessionCreator: DbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

    def makeHandlers(self):
        """ Make Handlers

        In this method we start all the RPC handlers
        start() returns an instance of it's self so we can simply yield the result
        of the start method.

        """

        yield self.loadSearchIndexChunks.start(funcSelf=self)
        yield self.loadSearchObjectChunks.start(funcSelf=self)
        logger.debug("RPCs started")

    # -------------
    @vortexRPC(peekServerName, acceptOnlyFromVortex=peekClientName, timeoutSeconds=60,
               additionalFilt=searchFilt, deferToThread=True)
    def loadSearchIndexChunks(self, offset: int, count: int
                              ) -> List[EncodedSearchIndexChunk]:
        """ Update Page Loader Status

        Tell the server of the latest status of the loader

        """
        session = self._dbSessionCreator()
        try:
            chunks = (session
                      .query(EncodedSearchIndexChunk)
                      .order_by(EncodedSearchIndexChunk.id)
                      .offset(offset)
                      .limit(count)
                      .yield_per(count))

            return list(chunks)

        finally:
            session.close()

    # -------------
    @vortexRPC(peekServerName, acceptOnlyFromVortex=peekClientName, timeoutSeconds=60,
               additionalFilt=searchFilt, deferToThread=True)
    def loadSearchObjectChunks(self, offset: int, count: int
                               ) -> List[EncodedSearchObjectChunk]:
        """ Update Page Loader Status

        Tell the server of the latest status of the loader

        """
        session = self._dbSessionCreator()
        try:
            chunks = (session
                      .query(EncodedSearchObjectChunk)
                      .order_by(EncodedSearchObjectChunk.id)
                      .offset(offset)
                      .limit(count)
                      .yield_per(count))

            return list(chunks)

        finally:
            session.close()
