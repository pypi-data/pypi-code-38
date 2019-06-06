import logging

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

from peek_plugin_tutorial._private.agent.RpcForServer import RpcForServer

logger = logging.getLogger(__name__)


class ServerToAgentRpcCallExample:
    def start(self):
        # kickoff the example
        # Tell the reactor to start it in 1 second, we shouldn't do things like this in
        # the plugins start method.
        reactor.callLater(20, self.run)

        return self

    @inlineCallbacks
    def run(self):
        # Call the agents RPC method
        result = yield RpcForServer.subInts(7, kwval1=5)
        logger.debug("seedInt result = %s (Should be 2)", result)

    def shutdown(self):
        pass
