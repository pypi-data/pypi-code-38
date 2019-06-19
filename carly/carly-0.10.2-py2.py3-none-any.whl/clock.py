from __future__ import print_function

from twisted.internet import reactor
from twisted.internet.defer import Deferred, inlineCallbacks

DEFAULT_TIMEOUT = 0.2


def withTimeout(deferred, timeout=None):
    if timeout is None:
        timeout = DEFAULT_TIMEOUT
    return deferred.addTimeout(timeout, reactor)


def cancelDelayedCalls(expected=2):
    """
    :param expected:
      The number of calls to cancel. If the number found does not match this,
      none of them will be cancelled so that trial's cleanup can tell you
      more about them.

      Why the default of 2? Hopefully you're only testing one delayed calll
      generator at a time, and there's one for trial's 2 minute timeout.
    """
    calls = reactor.getDelayedCalls()
    strings = []
    for call in calls:
        strings.append(str(call))
        call.cancel()
    if len(calls) != expected:
        raise AssertionError(
            '\n\nExpected {} delayed calls, found {}: {}'.format(
                expected, len(calls), strings
        ))


def _pump():
    d = Deferred()
    reactor.callLater(0, lambda: d.callback(None))
    return d


@inlineCallbacks
def advanceTime(seconds):
    """
    Advance the reactor time by the number of seconds or partial seconds
    specified.
    """
    yield _pump()
    now = reactor.seconds()
    for call in reactor.getDelayedCalls():
        currentSecondsFromNow = call.getTime() - now
        newSecondsFromNow = max(0, currentSecondsFromNow - seconds)
        call.reset(newSecondsFromNow)
    # give the reactor a chance to run calls we're brought forward:
    yield _pump()
