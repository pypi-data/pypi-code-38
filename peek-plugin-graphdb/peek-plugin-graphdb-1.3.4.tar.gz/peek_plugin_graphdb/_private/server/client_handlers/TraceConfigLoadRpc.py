import logging
from typing import List

from peek_plugin_graphdb.tuples.GraphDbTraceConfigTuple import GraphDbTraceConfigTuple
from sqlalchemy.orm import joinedload
from vortex.rpc.RPC import vortexRPC

from peek_plugin_base.PeekVortexUtil import peekServerName, peekClientName
from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_plugin_graphdb._private.PluginNames import graphDbFilt
from peek_plugin_graphdb._private.storage.GraphDbTraceConfig import GraphDbTraceConfig

logger = logging.getLogger(__name__)


class TraceConfigLoadRpc:
    def __init__(self, dbSessionCreator: DbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

    def makeHandlers(self):
        """ Make Handlers

        In this method we start all the RPC handlers
        start() returns an instance of it's self so we can simply yield the result
        of the start method.

        """

        yield self.loadTraceConfigs.start(funcSelf=self)
        logger.debug("RPCs started")

    # -------------
    @vortexRPC(peekServerName, acceptOnlyFromVortex=peekClientName, timeoutSeconds=60,
               additionalFilt=graphDbFilt, deferToThread=True)
    def loadTraceConfigs(self, offset: int, count: int) -> List[GraphDbTraceConfigTuple]:
        """ Load Trace Configs

        Allow the client to incrementally load the trace configs.

        """
        session = self._dbSessionCreator()
        try:
            ormObjs = (session
                      .query(GraphDbTraceConfig)
                      .options(joinedload(GraphDbTraceConfig.modelSet))
                      .options(joinedload(GraphDbTraceConfig.rules))
                      .order_by(GraphDbTraceConfig.id)
                      .offset(offset)
                      .limit(count))

            return [ormObj.toTuple() for ormObj in ormObjs]

        finally:
            session.close()
