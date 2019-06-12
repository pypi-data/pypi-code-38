'''
Provides extra debugging about which reactor calls are taking a long time.

Note that this adds the overhead of two system clock calls per function call
that the reactor makes.
'''
from contextlib import contextmanager
import cProfile
import logging
import pstats
from io import StringIO

from twisted.internet import base, defer, reactor
from twisted.python import reflect

log = logging.getLogger(__name__)

try:
    from twisted.internet.iocpreactor import reactor as iocpreactor
except ImportError:
    iocpreactor = None

try:
    from twisted.internet import epollreactor
except ImportError:
    epollreactor = None

try:
    from twisted.internet import selectreactor
except ImportError:
    selectreactor = None


profile_everything = False


class FunctionTimer(object):
    '''
    Used to time functions and log those which take longer than a particular
    threshold. If an inner function is also being logged, this is not counted
    towards the outer function's total.

    This is useful for example when deferreds are called back - any queued
    callbacks are called immediately, within the d.callback() call, but if
    they're wrapped it won't be counted towards the caller's total.
    '''
    threshold = 0.1

    def __init__(self):
        self.call_stack = []
        self.message = None
        self.started = 0

    @contextmanager
    def activate(self, message):
        now = reactor.seconds()
        self.call_stack.append((now - self.started, self.message))
        self.started = now
        self.message = message

        pr = None
        if profile_everything:
            pr = cProfile.Profile()
            pr.enable()

        try:
            yield
        finally:
            s = None
            if pr:
                pr.disable()
                s = StringIO()
                ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
                ps.print_stats(40)

            now = reactor.seconds()
            t = now - self.started
            self.log_activity(t, self.message, s)
            t, self.message = self.call_stack.pop()
            self.started = now - t

    def log_activity(self, t, message, s):
        if t > self.threshold:
            if s:
                message += '\n' + s.getvalue()
            log.warning('%.2fs: %s', t, message)

    def wrap(self, fn):
        '''
        Wraps the function so that when it is called, its execution will be
        timed with this timer.
        '''
        def wrapper(*args, **kwargs):
            arg_strings = [repr(arg) for arg in args]
            arg_strings += ['%s=%r' % (k, v) for (k, v) in kwargs.items()]
            name = self.get_name(fn)
            message = ('calling %s(%s)' % (name, ', '.join(arg_strings)))
            with self.activate(message):
                return fn(*args, **kwargs)
        return wrapper

    def get_name(self, fn):
        try:
            return reflect.fullyQualifiedName(fn)
        except:
            return str(fn)

function_timer = FunctionTimer()


def timed_add_callbacks(self, callback, errback=None, *args, **kwargs):
    '''
    Replaces Deferred.addCallbacks so that callbacks are timed.
    '''
    callback = function_timer.wrap(callback)
    if errback is not None:
        errback = function_timer.wrap(errback)
    return monkey_patcher.deferred_addCallbacks(
        self, callback, errback, *args, **kwargs)


def timed_delayed_call(self, time, func, *args, **kwargs):
    '''
    Replaces DelayedCall.__init__ so that delayed calls are timed.
    '''
    func = function_timer.wrap(func)
    return monkey_patcher.delayedCall_init(self, time, func, *args, **kwargs)


class MonkeyPatcher(object):
    def __init__(self):
        self.patched = False
        self.deferred_addCallbacks = None
        self.delayedCall_init = None
        self.ePollReactor_doReadOrWrite = None

    def on(self):
        if self.patched:
            return
        self.deferred_addCallbacks = defer.Deferred.addCallbacks
        self.delayedCall_init = base.DelayedCall.__init__
        if epollreactor:
            self.ePollReactor_doReadOrWrite = (
                epollreactor.EPollReactor._doReadOrWrite)
        if selectreactor:
            self.selectReactor_doReadOrWrite = (
                selectreactor.SelectReactor._doReadOrWrite)
        if iocpreactor:
            self.iocpReactor_callEventCallback = (
                iocpreactor.IOCPReactor._callEventCallback)
        self.patched = True
        defer.Deferred.addCallbacks = timed_add_callbacks
        base.DelayedCall.__init__ = timed_delayed_call
        if epollreactor:
            epollreactor.EPollReactor._doReadOrWrite = function_timer.wrap(
                self.ePollReactor_doReadOrWrite)
        if selectreactor:
            selectreactor.SelectReactor._doReadOrWrite = function_timer.wrap(
                self.selectReactor_doReadOrWrite)
        if iocpreactor:
            iocpreactor.IOCPReactor._callEventCallback = function_timer.wrap(
                self.iocpReactor_callEventCallback)

    def off(self):
        if not self.patched:
            return
        defer.Deferred.addCallbacks = self.deferred_addCallbacks
        base.DelayedCall.__init__ = self.delayedCall_init
        if epollreactor:
            epollreactor.EPollReactor._doReadOrWrite = (
                self.ePollReactor_doReadOrWrite)
        if selectreactor:
            selectreactor.SelectReactor._doReadOrWrite = (
                self.selectReactor_doReadOrWrite)
        if iocpreactor:
            iocpreactor.IOCPReactor._callEventCallback = (
                self.iocpReactor_callEventCallback)
        self.patched = False

monkey_patcher = MonkeyPatcher()


def start(profiling=False):
    global profile_everything
    profile_everything = profiling
    monkey_patcher.on()


def stop():
    monkey_patcher.off()


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    import time
    monkey_patcher.on()

    def wait(*args, **kwargs):
        time.sleep(.6)
        return 7
    reactor.callLater(.2, wait, 'X')
    d = defer.succeed(4)
    d.addCallback(wait, 'Y')

    reactor.run()
