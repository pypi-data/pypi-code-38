"""
.. module::timer
   :platform: Cross platform
   :synopsis: Contains the Timer class.

.. moduleauthor:: Drason "Emmy" Chow <emchow@iu.edu>

"""

from timeit import default_timer
from time import process_time
from units import Units

class Timer:
    """High precision timer utility class that makes it easy to time events elegantly"""

    def __init__(self, t0=None, units=Units.SEC, start=False, count_sleep=True):
        """
        Creates a timer object.

        :param t0: starting time of your timer in units of your preferred timing function. Defaults to have timer start at 0
        :type t0: float, None

        :param units: enum valued time unit. Can be seconds, milliseconds, microseconds, or nanoseconds
        :type units: Units

        :param start: Whether or not your timer is started after instantiation. False by default.
        :type start: bool

        :param count_sleep: The timer counts time the process is asleep as having elapsed. True by default.
        :type count_sleep: bool

        :returns: newly instantitated Timer object
        :rtype: Timer
        """

        if (count_sleep):
            self._clock = default_timer
        else:
            self._clock = process_time


        if (t0 is None):
            self._t0 = self._clock()
        else:
            self._t0 = t0

        self._units = units
        self._paused = not(start)

        self._mem = 0

    @staticmethod
    def wait(duration, units=Units.SEC, count_sleep=False):
        """
        Causes the current thread to pause for the indicated duration.

        :param duration: the duration to wait in your chosen units
        :param units: time units from the Units enum.
        """
        clock = default_timer if not count_sleep else process_time
        t0 = clock()

        while((clock() - t0) * units.value < duration):
            pass


    def set_units(self, units):
        """ Set the units for the timer to use """

        self._units = units

    def elapsed(self):
        """
        Compute the amount of time elapsed since the last elapsed time reset

        :return: time elapsed in the timer's units (timer - t0)
        :rtype: float
        """
        if (self._paused):
            return (self._mem)
        else:
            return ((self._clock() - self._t0) * self._units.value + self._mem)

    def elapsed_raw(self):
            if (self._paused):
                return self._mem
            else:
                return (self._clock() - self._t0 + self._mem)


    def reset(self, pause=True):
        """
        Resets the time elapsed. Currently there is no way to count cycles independently of time elapsed. This is a feature
        planned for a future update.

        :param pause: pause the timer after resetting. default value is True.
        :rtype pause: bool
        """
        self._paused = pause

        self._mem = 0
        self._t0 = self._clock()

    def start(self):
        """ Start the timer if it's paused. Does nothing if the timer is already started """

        if (self._paused):
            self._paused = False
            self._t0 = self._clock()

    def stop(self):
        """ Stops the timer if it's not paused. Does nothing if the timer is already paused """

        if(not self._paused):
            self._mem = self.elapsed()
            self._paused = True

def main():
    """
    Rough sanity checker to make sure the code is working correctly. Always uses seconds.

    Test by running this program with python and providing a number in seconds as a parameter to the program.
    """

    import sys
    import time

    if (len(sys.argv) != 2):
        print("Usage: python3 timer.py wait_seconds")
        sys.exit(1)

    timer = Timer(units=Units.SEC, start=False)
    times = []
    for i in range(10):
        timer.start()
        try:
            time.sleep(float(sys.argv[1]))
        except ValueError:
            raise ValueError

        times.append(timer.elapsed() - float(sys.argv[1]))
        print("{}/10 Latency: {}".format(i + 1, times[-1]))
        timer.reset()

    import math
    avgLatency = math.fsum(times) / 10
    print("Done.\nAverage latency: {}\nPercent Latency: {}".format(avgLatency, avgLatency/float(sys.argv[1])))

if (__name__ == '__main__'):
    print("Beginning test...")

    main()


