from cmndr import Middleware

class StatsMiddleware(Middleware):
    def __init__(self, stats):
        self._stats = stats

    def execute(self, command, next_callable):
        namespace = command.__module__.split('.')[1] + '.' + command.__class__.__name__.lower()
        stats = self._stats

        stats.incr(namespace, 1)
        with stats.time(namespace):
            ret = next_callable(command)

        return ret
