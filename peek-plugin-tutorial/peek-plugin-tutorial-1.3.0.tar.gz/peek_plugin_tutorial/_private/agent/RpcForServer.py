import logging

from peek_plugin_base.PeekVortexUtil import peekAgentName
from peek_plugin_tutorial._private.PluginNames import tutorialFilt
from vortex.rpc.RPC import vortexRPC

logger = logging.getLogger(__name__)


class RpcForServer:
    def __init__(self):
        pass

    def makeHandlers(self):
        """ Make Handlers

        In this method we start all the RPC handlers
        start() returns an instance of it's self so we can simply yield the result
        of the start method.

        """

        yield self.subInts.start(funcSelf=self)
        logger.debug("Server RPCs started")

    # -------------
    @vortexRPC(peekAgentName, additionalFilt=tutorialFilt)
    def subInts(self, val1, kwval1=9):
        """ Add Ints

        This is the simplest RPC example possible.

        :param val1: A value to start with
        :param kwval1: The value to subtract
        :return: One value minus the other

        """
        return val1 - kwval1
