import logging

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

from peek_plugin_tutorial._private.server.agent_handlers.RpcForAgent import RpcForAgent
from peek_plugin_tutorial._private.storage.StringIntTuple import StringIntTuple

logger = logging.getLogger(__name__)


class AgentToServerRpcCallExample:
    def start(self):
        # kickoff the example
        # Tell the reactor to start it in 1 second, we shouldn't do things like this in
        # the plugins start method.
        reactor.callLater(5, self.runWithInlineCallback)

        # Return self, to make it simpler for the AgentEntryHook
        return self

    @inlineCallbacks
    def runWithInlineCallback(self):
        """ Run With Inline Callbacks

        To understand what the :code:`@inlineCallbacks` decorator does, you can read
        more in the twisted documentation.

        This is the simplest way to go with asynchronous code.

        Yield here, will cause the flow of code to return to the twisted.reactor
        until the deferreds callback or errback is called.

        The errback will cause en exception, which we'd catch with a standard
        try/except block.

        """

        # The :code:`@vortexRPC` decorator wraps the :code:`RpcForAgent.updateStatus`
        # method with an instance of the :code:`_VortexRPC` class,
        # this class has a :code:`__call__` method implemented, that is what we're
        # calling here.
        #
        # So although it looks like we're trying to call a class method, that's not what's
        # happening.
        yield RpcForAgent.updateStatus("Agent RPC Example Started")

        seedInt = 5
        logger.debug("seedInt = %s", seedInt)

        for _ in range(5):
            seedInt = yield RpcForAgent.addInts(seedInt, kwval1=7)
            logger.debug("seedInt = %s", seedInt)

        # Move onto the run method.
        # We don't use yield here, so :code:`runWithInlineCallback` will continue on and
        # finish
        self.run()
        logger.debug("runWithInlineCallback finished")

    def run(self):
        """ Run

        In this method, we call some RPCs and handle the deferreds.

        We won't be using @inlineCallbacks here. We will setup all the calls and
        callbacks, then the run method will return. The calls and callbacks will happen
        long after this method finishes.

        """

        stringInt = StringIntTuple(int1=50, string1="Created from Agent RPC")

        d = RpcForAgent.addStringInt(stringInt)

        # the deferred will call the lambda function,
        #   "_" will be the result of "addStringInt, which we ignore
        #   the lambda function calls RpcForAgent.updateStatus,
        #   which will return a deferred
        #
        # Returning a deferred from a callback is fine, it's just merilly processed
        d.addCallback(lambda _: RpcForAgent.updateStatus("Agent RPC Example Completed"))

        # Unless you have a good reason, always return the last deferred.
        return d

    def shutdown(self):
        pass
