import statsd

from strongr.core.stats.abstractstats import AbstractStats

class StatsDDriver(AbstractStats):
    _statsd = None

    def __init__(self, config):
        self._statsd = statsd.StatsClient(**config)

    def decr(self, namespace, amount, rate=1):
        self._statsd.decr(namespace, amount, rate)

    def gauge(self, namespace, amount, rate=1, delta=False):
        self._statsd.gauge(namespace, amount, rate, delta)

    def set(self, namespace, arr):
        self._statsd.set(namespace, arr)

    def time(self, namespace):
        return self._statsd.timer(namespace)

    def timing(self, namespace, timems):
        self._statsd.timing(namespace, timems)

    def incr(self, namespace, amount, rate=1):
        self._statsd.incr(namespace, amount, rate)
