"""
.. module::cycle_timer
   :platform: Cross Platform
   :synposis: Contains the CycleTimer class

.. moduleauthor:: Drason "Emmy" Chow <emchow@iu.edu>
"""

from timer import Timer
from units import Units
from math import floor
from timeit import default_timer

class TimeMismatch(Exception):
    pass

class CycleTimer(Timer):

    """Inherits from Timer. An elegant way of measuring cycles of a specified length"""

    def __init__(self, interval, strict=False, grace_period=1, **kwargs):
        """
        Instantiates a CycleTimer object

        :param interval: interval between timer cycles. interval 0 will raise a ValueError
        :type interval: float

        :param strict: if true, the timer will raise an exception if an unacceptable number of clock cycles is skipped.
        False by default.
        :type strict: bool

        :param grace_period: maximum acceptable time between calls to elapsed() or tick(). Good if lag in a system is
        unacceptable.
        :type grace_period: float

        :returns: newly instantiated CycleTimer object
        :rtype: CycleTimer

        """

        super().__init__(**kwargs)

        self._interval = interval
        self._strict = strict
        self._grace_period = grace_period

        self._cycles = 0

        #Call to elapsed sets _cycles
        self.elapsed()
    def set_strictness(self, strict=False):
        """
        Sets the strictness of the timer.

        :param strict: The strictness of the timer. False by default.
        :type strict: bool
        """

        self._strict = strict

    def set_interval(self, interval, align=False, redefine_past=False):
        """
        Set the interval between timer cycles

        :param interval: interval between timer cycles in the timer's units
        :type interval: float

        :param align: whether or not to wait for the current timer cycle to
        complete. False sets the interval immediately. Defaults to false
        :type align: bool

        :param redefine_past: redefines all past cycles to use the new interval,
        changing the value of elapsed.  Defaults to false.
        :type redefine_past: bool
        """

        if (align):
            while(not self.tick()):
                pass

        if (redefine_past):
            self._mem *= (self._interval / interval)
        else:
            self._mem = self.elapsed()
            self._t0 = default_timer()

        self._interval = interval


    def set_grace_period(self, grace_period):
        """
        Sets the grace period of the timer.

        :param grace_period: the grace period of the time
        :type grace_period: float
        """

        self._grace_period = grace_period

    def elapsed(self):
        """
        Compute total fractional number of timer cycles since the last set

        :raises TimerMismatch: Exception raised in strict timers that exceed the grace period between calls to elapsed()
        or tick()

        :returns: Fractional number of timer cycles elapsed
        :rtype: float
        """

        try:
            if (self._paused):

                return self._mem

            else:

                now = ((default_timer() - self._t0) * self._units.value) / self._interval + self._mem

                #expected difference is 1
                if (self._strict):
                    if((now - self._cycles) > (self._grace_period + 1)):
                        raise TimeMismatch("Timer mistmatch. One or more clock cycle was skipped.")
                self._cycles = now
                return now

        except ValueError:
            print("Cycles cannot be counted with interval 0 (default interval)")
            raise ValueError

    def elapsed_discrete(self):
        """
        Compute whole number of timer cycles since the last set

        :returns: Whole number of timer cycles elapsed
        :rtype: int
        """
        return floor(self.elapsed())

    def stop(self):
        """Pauses the timer noting the current number of cycles"""
        super().stop()
        self._cycles = self._mem

    def tick(self):
        """
        Tells whether one or more clock cycles have been completed since the last call tick() or cycles()

        :returns: True or False depending on whether or not one or more whole clock cycles have been completed since the last call
        to tick() or elapsed()
        :rtype: bool
        """
        return (floor(self._cycles) < self.elapsed_discrete())

def main():
    import sys
    import time
    import math

    if(len(sys.argv) != 2):
        print("Usage: python3 CycleTimer.py wait_interval")
        sys.exit(1)

    test_interval = float(sys.argv[1])

    print("Using test interval of {}".format(test_interval))
    timer = CycleTimer(interval=test_interval, units=Units.SEC, start=False)

    times = []
    timer.start()
    for i in range(5):
        time.sleep(test_interval)
        times.append(timer.elapsed() - 1)
        print("{}/5 Latency: {}".format(i + 1, times[-1]))
        timer.reset(pause=False)
    timer.stop()
    print("Average Latency: {}".format(math.fsum(times) / 5))

    timer.start()
    time.sleep(test_interval)
    old_time = timer.elapsed()
    timer.set_interval(interval=test_interval * .5, redefine_past=True)
    print("Testing interval set. old={}, new={}".format(old_time, timer.elapsed()))

    timer.reset()
    times = []

    print("Testing new interval {}...".format(.5 * test_interval))

    timer.start()
    for i in range(5):
        time.sleep(test_interval * .5)
        times.append(timer.elapsed() - 1)
        print("{}/5 Latency: {}".format(i + 1, times[-1]))
        timer.reset(pause=False)

    timer.stop()
    print("Average Latency: {}".format(math.fsum(times) / 5))

    print("Testing strict...")

    timer.set_strictness(strict=True)
    timer.start()
    time.sleep(test_interval)
    try:
        timer.tick()
    except TimeMismatch:
        print("Strictness test successful. End of tests.")
        sys.exit(0)
    print("Srictness test unsuccessful. End of tests.")

if (__name__ == '__main__'):
    print("Beginning test...")

    main()
