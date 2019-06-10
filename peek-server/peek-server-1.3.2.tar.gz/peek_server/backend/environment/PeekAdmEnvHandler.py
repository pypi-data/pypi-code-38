'''
Created on 09/07/2014

@author: synerty
'''
from peek_server.storage import dbConn
from peek_server.storage.PeekEnv import PeekEnvServer, PeekEnvAgent, PeekEnvWorker, \
    PeekEnvClient
from vortex.sqla_orm.OrmCrudHandler import OrmCrudHandler, OrmCrudHandlerExtension

# -----------------------------------------------------------------------------
# Servers
serverListDataKey = {
    'plugin': 'peek_server',
    'key': "peakadm.env.server.list.data"
}


class EnvServerListHandler(OrmCrudHandler):
    pass


envServerListHandler = EnvServerListHandler(dbConn.ormSessionCreator,
                                            PeekEnvServer,
                                            serverListDataKey,
                                            retreiveAll=True)


@envServerListHandler.addExtension(PeekEnvServer)
class _EnvServerListHandlerExtension(OrmCrudHandlerExtension):
    def afterUpdateCommit(self, tuple_, tuples, session, payloadFilt):
        # from peek.api.client.ClientGridHandler import clientGridHandler
        # reactor.callLater(0.0, clientGridHandler.reload)
        return True


# -----------------------------------------------------------------------------
# workers
workerListDataKey = {
    'plugin': 'peek_server',
    'key': "peakadm.env.worker.list.data"
}


class EnvWorkerListHandler(OrmCrudHandler):
    pass


envWorkerListHandler = EnvWorkerListHandler(dbConn.ormSessionCreator,
                                            PeekEnvWorker,
                                            workerListDataKey,
                                            retreiveAll=True)


@envWorkerListHandler.addExtension(PeekEnvWorker)
class _EnvWorkerListHandlerExtension(OrmCrudHandlerExtension):
    def afterUpdateCommit(self, tuple_, tuples, session, payloadFilt):
        # from peek.api.client.ClientGridHandler import clientGridHandler
        # reactor.callLater(0.0, clientGridHandler.reload)
        return True

# -----------------------------------------------------------------------------
# agents
agentListDataKey = {
    'plugin': 'peek_server',
    'key': "peakadm.env.agent.list.data"
}

class EnvAgentListHandler(OrmCrudHandler):
    pass

envAgentListHandler = EnvAgentListHandler(dbConn.ormSessionCreator,
                                          PeekEnvAgent,
                                          agentListDataKey,
                                          retreiveAll=True)

@envAgentListHandler.addExtension(PeekEnvAgent)
class _EnvAgentListHandlerExtension(OrmCrudHandlerExtension):
    def afterUpdateCommit(self, tuple_, tuples, session, payloadFilt):
        return True

# -----------------------------------------------------------------------------
# agents
clientListDataKey = {
    'plugin': 'peek_server',
    'key': "peakadm.env.client.list.data"
}


class EnvClientListHandler(OrmCrudHandler):
    pass


envClientListHandler = EnvClientListHandler(dbConn.ormSessionCreator,
                                          PeekEnvClient,
                                           clientListDataKey,
                                          retreiveAll=True)


@envClientListHandler.addExtension(PeekEnvClient)
class _EnvClientListHandlerExtension(OrmCrudHandlerExtension):
    def afterUpdateCommit(self, tuple_, tuples, session, payloadFilt):
        return True
