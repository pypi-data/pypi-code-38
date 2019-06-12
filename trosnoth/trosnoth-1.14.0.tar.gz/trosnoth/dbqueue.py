'''
Provides utilities for deferred writing to the database over time, so as not to
cause too much interruption to the game in progress.
'''

import logging

from twisted.internet import defer, reactor

log = logging.getLogger(__name__)


DELAY = 0.01

queue = defer.DeferredQueue()
initialised = False
stopping = False


@defer.inlineCallbacks
def init():
    '''
    Initialises the deferred database queue.
    '''
    global initialised
    if initialised:
        return
    initialised = True

    reactor.addSystemEventTrigger('before', 'shutdown', teardown)

    while queue or not stopping:
        fn = yield queue.get()
        log.debug('dbqueue: running %r', fn)
        try:
            yield fn()
        except:
            log.exception('Error in queued database function')

        yield wait()


def add(fn):
    '''
    Adds the given function to the database queue.
    '''
    assert initialised
    queue.put(fn)


def wait():
    '''
    Returns a deferred which will fire when the next database command should be
    run. Database callback functions with lots of database work to do should
    call this to break up the work and avoid blocking.
    '''
    assert initialised
    d = defer.Deferred()
    if stopping:
        d.callback(None)
    else:
        reactor.callLater(DELAY, d.callback, None)
    return d


def teardown():
    assert initialised

    global stopping
    stopping = True

    d = defer.Deferred()
    log.info('Stopping database queue...')

    @queue.put
    def queueIsEmpty():
        log.info('Database queue stopped')
        d.callback(None)

    return d
