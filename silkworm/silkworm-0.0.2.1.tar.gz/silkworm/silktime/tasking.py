"""
.. module:: tasking
   :platform: Unix, Windows, OS X
   :synopsis: Utilities for timing functions

.. moduleauthor:: Drason "Emmy" Chow <emchow@iu.edu>
"""

from timer import Timer
from cycle_timer import CycleTimer
from units import Units

import time
import threading
from threading import Thread


class FormatException(Exception):
    pass

def iterate(n=None, interval=0, units=Units.SEC, blocking=False):
    """
    Decorator function for simple function iteration

    :param n: the number of iterations to complete
    :type n: int, None

    :param interval: delay between iterations. Default is 0
    :type interval: int

    :param units: the units your interval is in
    :type units: Units

    :param blocking: Whether the function call blocks the current thread.
    Default is false
    :type blocking: bool

    :raises: ValueError
    """

    def decorator(func):
        def wrapper(*args, **kwargs):

            def schedule():
                if (n is None):
                    while True:
                        func(*args, **kwargs)
                        Timer.wait(interval, units)
                else:
                    if (n < 0):
                        raise ValueError("n cannot be less than 0.")
                    else:
                        for i in range(n):
                            func(*args, **kwargs)

                            if (i + 1 < n):
                                Timer.wait(interval, units)

            thread = threading.Thread(target=schedule)
            thread.start()

            if (blocking):
                thread.join()

        return wrapper
    return decorator


class TimedTask(CycleTimer):
    """Class that allows controlled execution of tasks on a set interval a number iterations"""

    def __init__(self, tasks, iterations=None, timeout=None,
                 blocking=False, *args, **kwargs):
        """
        Instantiates TimedTask object.

        :param tasks: a list of function objects that will be executed in order at the predefined interval
        :type tasks: list

        :param iterations: the maximum number of iterations to run the tasks
        :type iterations: int, None

        :param timeout: the maximum amount of time in your chosen units to run the tasks
        :type timeout: float, None

        :param blocking: whether or not the tasks should block execution of the current thread
        :type blocking: bool

        :rtype: TimedTask
        """

        super().__init__(*args, **kwargs)

        self._iterations = iterations
        self._timeout = timeout
        self._blocking = blocking
        self._tasks = tasks
        self._i = 0

        if (not self._paused):
            self.start()

    def _stop_signal(self):
        """Signals the thread to stop execution after the current iteration is done."""

        if (self._paused):
            return True

        if (not self._iterations is None):
           if (self.elapsed_discrete() >= self._iterations):
               return True

        if (not self._timeout is None):
            if (self.elapsed() * self._interval >= self._timeout):
                return True

        return False

    def _schedule(self):
        """
        Defines the schedule of a single interval, which is:

        1. Tasks executed in order
        2. Check to see if _stop_signal() is True
        3. Wait for the next interval
        """

        while(True):
            for task in self._tasks:
                task()

            if (self._stop_signal()):
                return

            while(not self.tick()):
                pass

    def start(self):
        """Starts the timer and starts the execution of of the defined schedule"""
        super().start()

        thread = threading.Thread(target=self._schedule)
        thread.start()

        if (self._blocking):
            thread.join()

def main():
    """Very rudimentary tester that checks sanity by executing 10 iterations with interval 2"""
    timed_task = TimedTask(interval=2,
                           tasks=[lambda: print("hi")],
                           iterations=10,
                           start=True)

if (__name__ == '__main__'):
    main()
