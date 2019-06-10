import time


class TokenBucket(object):
    def __init__(self, limit, interval_seconds, do_once_when_exhausted=None):
        self._remaining = limit
        self._initial_value = limit
        self._last_reset = time.time()
        self._interval = interval_seconds
        self._do_once_when_exhausted = do_once_when_exhausted
        self._do_once_when_exhausted_performed = False

    def _is_exhausted(self):
        if time.time() - self._last_reset >= self._interval:
            self._last_reset = time.time()
            self._remaining = self._initial_value
            self._do_once_when_exhausted_performed = False
        return self._remaining < 0

    def do_if_available(self, func):
        self._remaining -= 1
        if self._is_exhausted():
            if self._do_once_when_exhausted is not None and self._do_once_when_exhausted_performed is False:
                self._do_once_when_exhausted_performed = True
                self._do_once_when_exhausted()
            return

        func()
