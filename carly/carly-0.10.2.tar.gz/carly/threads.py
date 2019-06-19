from time import sleep

from twisted.internet import reactor
from twisted.internet.threads import deferToThread

from .clock import withTimeout


def pendingIsEmpty():
    while True:
        stats = reactor.threadpool._team.statistics()
        if not (stats.backloggedWorkCount or stats.busyWorkerCount > 1):
            break
        sleep(0.001)


def waitForThreads(timeout=None):
    return withTimeout(deferToThread(pendingIsEmpty), timeout)
