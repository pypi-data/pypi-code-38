import ctypes
import ctypes.wintypes as cwt
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)


# From Stack Overflow
# User linusg https://stackoverflow.com/users/5952681/linusg
# https://stackoverflow.com/a/38463185/2690232
class MonoClock(object):
    def __init__(self):
        self._reference_counter = self.get_ticks()
        self.frequency = cwt.LARGE_INTEGER()
        kernel32.QueryPerformanceFrequency(ctypes.byref(self.frequency))
        self.frequency = float(self.frequency.value)

    def get_ticks(self):
        current_counter = cwt.LARGE_INTEGER()
        kernel32.QueryPerformanceCounter(ctypes.byref(current_counter))
        return current_counter

    def get_time(self):
        return (self.get_ticks().value - self._reference_counter.value) / self.frequency

    def getTime(self):
        return self.get_time()

    @property
    def start_time(self):
        return self._reference_counter.value / self.frequency
