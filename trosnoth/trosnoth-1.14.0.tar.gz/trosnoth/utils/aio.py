import asyncio
import logging

from twisted.internet import defer, reactor
from twisted.python.failure import Failure

log = logging.getLogger(__name__)


def _catch(failure):
    # Without this, all traceback information from within the Twisted code
    # vanishes.
    if len(failure.value.args) > 1:
        return failure

    description = '{}\n--- deferred stack ---\n{}'.format(
        failure.value, failure.getTraceback())

    try:
        exc = type(failure.value)(description)
    except Exception:
        return failure
    return Failure(exc)


def check_reactor():
    if 'asyncio' not in type(reactor).__name__.lower():
        import sys
        sys.exit(
            'Asyncio reactor not installed in Twisted! (Saw {} instead.) '
            'Exiting.'.format(type(reactor).__name__))


def as_future(d):
    # noinspection PyUnreachableCode
    if __debug__:
        check_reactor()

    return d.addErrback(_catch).asFuture(asyncio.get_event_loop())


def as_deferred(f):
    # noinspection PyUnreachableCode
    if __debug__:
        check_reactor()

    return defer.Deferred.fromFuture(asyncio.ensure_future(f))


async def cancel_task(task, *, loop=None):
    '''
    Coroutine which cancels the given task and does not return until the
    task finishes all cleanup from being cancelled.

    :param task: a task that has not already been awaited
    :param loop: the event loop. If ommitted, the current event loop is used.
    '''

    if loop is None:
        loop = asyncio.get_event_loop()

    done = loop.create_future()

    async def wrapper():
        try:
            await task
        finally:
            done.set_result(None)

    wrapper_task = asyncio.ensure_future(wrapper())
    loop.call_soon(wrapper_task.cancel)

    await done

