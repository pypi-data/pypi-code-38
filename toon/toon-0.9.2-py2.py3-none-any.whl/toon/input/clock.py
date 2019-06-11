import os

if os.name is 'nt':
    from ctypes import byref, c_int64, windll
    _fcounter = c_int64()
    _qpfreq = c_int64()
    windll.Kernel32.QueryPerformanceFrequency(byref(_qpfreq))
    _qpfreq = float(_qpfreq.value)
    _winQPC = windll.Kernel32.QueryPerformanceCounter

    def get_time():
        _winQPC(byref(_fcounter))
        return _fcounter.value / _qpfreq
else:
    from timeit import default_timer as get_time

class MonoClock(object):
    """A stripped-down version of psychopy's clock.MonotonicClock.

    I wanted to avoid importing pyglet on the remote process, in case that causes any headache.
    """
    def __init__(self, start_time=None):
        if not start_time:
            # this is sub-millisec timer in python
            self._start_time = get_time()
        else:
            self._start_time = start_time
    def get_time(self):
        """Returns the current time on this clock in secs (sub-ms precision)
        """
        return get_time() - self._start_time
    def getTime(self):
        """Alias get_time so we can set the default psychopy clock
        """
        return self.get_time()
    @property
    def start_time(self):
        return self._start_time

mono_clock = MonoClock()
    