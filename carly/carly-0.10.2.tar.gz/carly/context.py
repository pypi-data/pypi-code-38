from functools import partial

from twisted.internet.defer import (
    inlineCallbacks, gatherResults, maybeDeferred
)

from .clock import withTimeout, cancelDelayedCalls
from .hook import cleanup
from .threads import waitForThreads


class Context(object):

    def __init__(self):
        self.cleanups = {
            'connections': [],
            'listens': [],
        }

    def _cleanup(self, cleanups, timeout):
        deferreds = []
        for p in cleanups:
            d = p()
            deferreds.append(d)
            withTimeout(d, timeout)
        return gatherResults(deferreds)

    @inlineCallbacks
    def cleanup(self, timeout=None, threads=False, delayedCalls=None):
        yield self._cleanup(self.cleanups['connections'], timeout)
        yield self._cleanup(self.cleanups['listens'], timeout)
        cleanup()
        if threads:
            yield waitForThreads()
        if delayedCalls:
            cancelDelayedCalls(delayedCalls)

    def cleanupServers(self, *ports):
        self.cleanups['listens'].extend(
            partial(maybeDeferred, port.stopListening) for port in ports
        )

    def cleanupClient(self, client, close, timeout=None):
        if isinstance(close, str):
            name = close
            close = lambda client: getattr(client.clientProtocol, name)()
        self.cleanups['connections'].extend((
            partial(maybeDeferred, close, client),
            partial(client.clientProtocol.connectionLost.called, timeout=timeout),
            partial(client.serverProtocol.connectionLost.called, timeout=timeout),
        ))
