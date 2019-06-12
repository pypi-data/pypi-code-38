import logging
import weakref

from twisted.internet import reactor, task

log = logging.getLogger('utils.twist')


class WeakCallLater(object):
    '''
    Calls twisted.internet.reactor.callLater, but only maintains a weak
    reference to the object whose method is to be called. If the object is
    garbage collected, the callLater is cancelled.
    '''
    def __init__(self, delay, obj, attr, *args, **kw):
        self.obj = weakref.ref(obj, self._collect)
        self.attr = attr
        self.delayedCall = reactor.callLater(delay, self._call, *args, **kw)
        self.alive = True
        self._str = str(obj)

    def cancel(self):
        self.delayedCall.cancel()

    def getTime(self):
        return self.delayedCall.getTime()

    def delay(self, secondsLater):
        self.delayedCall.delay(secondsLater)

    def reset(self, secondsFromNow):
        self.delayedCall.reset(secondsFromNow)

    def active(self):
        return self.delayedCall.active()

    def _call(self, *args, **kwargs):
        obj = self.obj()
        if obj is None:
            log.warning(
                'callLater called after garbage collection: %s.%s' %
                (self._str, self.attr))
        else:
            try:
                return getattr(obj, self.attr)(*args, **kwargs)
            except Exception:
                log.exception('Error in WeakCallLater')

    def _collect(self, r):
        log.info('WeakCallLater: Collecting %s' % (self._str,))
        if self.delayedCall.active():
            self.delayedCall.cancel()
        self.alive = False


class WeakLoopingCall(object):
    '''
    Wraps a twisted.internet.task.LoopingCall, but only maintains a weak
    reference to the object whose method is to be called. If the object is
    garbage collected, the looping call is stopped.
    '''
    def __init__(self, obj, attr, *a, **kw):
        self.alive = True
        self.obj = weakref.ref(obj, self._collect)
        self.attr = attr
        self.loop = task.LoopingCall(self._call, *a, **kw)
        self._str = str(obj)

    @property
    def running(self):
        return self.loop.running

    def start(self, interval, now=True):
        self.loop.start(interval, now)

    def stop(self):
        if self.alive and self.loop.running:
            self.loop.stop()

    def _collect(self, r):
        log.info('WeakLoopingCall: Collecting %s' % (self._str,))
        self.alive = False
        if self.loop.running:
            self.loop.stop()

    def _call(self, *args, **kwargs):
        if self.alive:
            obj = self.obj()
            if obj is None:
                log.warning(
                    'Looping call called after garbage collection: %s.%s' %
                    (self._str, self.attr))
            else:
                try:
                    getattr(obj, self.attr)(*args, **kwargs)
                except Exception:
                    log.exception('Unhandled error in WeakLoopingCall')
