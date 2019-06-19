"""
Sends timing information to the logs
"""

import logging
from sparkplug.logutils import LazyLogger
from sparkplug.timereporters.base import Base, min_median_max

_log = LazyLogger(__name__)

class Logger(Base):
    def __init__(self, aggregation_count, level="DEBUG"):
        super(Logger, self).__init__(aggregation_count)
        self._exec_times = []
        self._erro_times = []
        self._wait_times = []
        # get the exact method for the correct logging level:
        self.logger = getattr(_log, str(level).lower())
        assert(callable(self.logger), "Logging level on timereporters.Logger does not resolve to anything useful")

    def append_exec(self, delta):
        self._exec_times.append(delta)
        if len(self._exec_times) >= self.aggregation_count :
            mn, md, mx = min_median_max(self._exec_times)
            del self._exec_times[:]
            self.logger("msg exec (min med max) ms: {:0.2f} {:0.2f} {:0.2f}".format(mn, md, mx))

    def append_erro(self, delta):
        self._erro_times.append(delta)
        if len(self._erro_times) >= self.aggregation_count :
            mn, md, mx = min_median_max(self._erro_times)
            del self._erro_times[:]
            self.logger("msg erro (min med max) ms: {:0.2f} {:0.2f} {:0.2f}".format(mn, md, mx))

    def append_wait(self, delta):
        self._wait_times.append(delta)
        if len(self._wait_times) >= self.aggregation_count :
            mn, md, mx = min_median_max(self._wait_times)
            del self._wait_times[:]
            self.logger("msg wait (min med max) ms: {:0.2f} {:0.2f} {:0.2f}".format(mn, md, mx))
