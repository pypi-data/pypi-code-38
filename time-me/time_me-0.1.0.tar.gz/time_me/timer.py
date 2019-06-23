from contextlib import contextmanager
from time import time
from warnings import warn


class Timer:
    """
    a simple structure to measure time differences
    >>> from time import sleep
    >>> from math import isclose
    >>> with Timer() as t:
    ...     sleep(0.1)
    ...     with t.pause():
    ...         sleep(0.1)
    ...         with t.resume():
    ...             sleep(0.1)
    ...         sleep(0.1)
    ...     sleep(0.1)
    >>> assert isclose(float(t), 0.3, abs_tol=0.02), str(t)
    """

    def __init__(self):
        self.since_pause_time = 0.0
        self.resume_time = None

    def is_running(self):
        return self.resume_time is not None

    def _resume(self):
        if self.is_running():
            raise Exception('timer is already running')
        self.resume_time = time()

    def _pause(self):
        t = time()
        if not self.is_running():
            raise Exception('timer is already paused')
        self.since_pause_time += (t - self.resume_time)
        self.resume_time = None

    def seconds(self):
        if self.is_running():
            raise Exception('timer is running')
        return self.since_pause_time

    @contextmanager
    def pause(self):
        self._pause()
        yield self
        self._resume()

    @contextmanager
    def resume(self):
        self._resume()
        yield self
        self._pause()

    def __float__(self):
        return self.seconds()

    def __lt__(self, other):
        return float(self) < float(other)

    def __gt__(self, other):
        return float(self) > float(other)

    def __le__(self, other):
        return float(self) <= float(other)

    def __ge__(self, other):
        return float(self) >= float(other)

    def __del__(self):
        if self.is_running():
            warn('timer deleted while running!')

    def __enter__(self):
        self._resume()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._pause()

    def __str__(self):
        if self.is_running():
            return f'Timer(running: >{self.since_pause_time} secs)'
        return f'Timer (paused: {float(self)} secs)'
