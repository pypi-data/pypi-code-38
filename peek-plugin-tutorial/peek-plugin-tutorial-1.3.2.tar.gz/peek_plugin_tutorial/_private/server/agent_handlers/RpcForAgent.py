import logging

from peek_plugin_base.PeekVortexUtil import peekServerName, peekAgentName
from peek_plugin_tutorial._private.PluginNames import tutorialFilt
from peek_plugin_tutorial._private.server.controller.MainController import MainController
from peek_plugin_tutorial._private.storage.StringIntTuple import StringIntTuple
from vortex.rpc.RPC import vortexRPC

logger = logging.getLogger(__name__)


class RpcForAgent:
    def __init__(self, mainController: MainController, dbSessionCreator):
        self._mainController = mainController
        self._dbSessionCreator = dbSessionCreator

    def makeHandlers(self):
        """ Make Handlers

        In this method we start all the RPC handlers
        start() returns an instance of it's self so we can simply yield the result
        of the start method.

        """

        yield self.addInts.start(funcSelf=self)
        yield self.updateStatus.start(funcSelf=self)
        yield self.addStringInt.start(funcSelf=self)
        logger.debug("RPCs started")

    # -------------
    @vortexRPC(peekServerName,
               acceptOnlyFromVortex=peekAgentName, additionalFilt=tutorialFilt)
    def addInts(self, val1, kwval1=9):
        """ Add Ints

        This is the simplest RPC example possible

        """
        return val1 + kwval1

    # -------------
    @vortexRPC(peekServerName,
               acceptOnlyFromVortex=peekAgentName, additionalFilt=tutorialFilt)
    def updateStatus(self, updateStr: str):
        """ Update Status

        The agent may be running something and send updates on occasion,
        tell these to the main controller, it can deal with them.

        """
        self._mainController.agentNotifiedOfUpdate(updateStr)

    # -------------
    @vortexRPC(peekServerName, acceptOnlyFromVortex=peekAgentName,
               additionalFilt=tutorialFilt, deferToThread=True)
    def addStringInt(self, stringInt: StringIntTuple):
        """ Insert a stringInt

        In this example RPC method, The agent tells the server to insert data into
        the database.

        It's a better design get the main controller to do things like this.
        It will know what else needs updating after the insert (IE, The observable)

        Notice the :code:`deferToThread=True` argument in :code:`@vortexRPC`?
        Because this code is blocking code, not written for twisted, we need to
        defer it to a thread so it doesn't block twisteds main reactor.

        As it's no longer in the twisted thread, all the code in this method
        should be standard blocking code.

        """
        session = self._dbSessionCreator()
        try:
            session.add(stringInt)

        except:
            session.rollback()
            raise

        finally:
            session.close()
