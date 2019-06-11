from timeit import default_timer as get_time


class MonoClock(object):
    """A stripped-down version of psychopy's clock.MonotonicClock.
    I wanted to avoid importing pyglet on the remote process, in case that causes any headache.
    """

    def __init__(self):
        self._start_time = get_time()

    def get_time(self):
        """Returns the current time on this clock in seconds (sub-ms precision)
        """
        return get_time() - self._start_time

    def getTime(self):
        """Alias for get_time, so we can set the default psychopy clock in logging.
        """
        return self.get_time()

    @property
    def start_time(self):
        return self._start_time
