"""utility functions and classes"""

from time import sleep
from threading import Thread, Event
from functools import partial
from os.path import getmtime
import traceback
import atexit
try:
    import RPi.GPIO as GPIO
except:
    pass

__all__ = ['fork', 'not_raising', 'IRQHandler', 'Poller', 'on_change', 'noop']


def fork(func):
    """run func asynchronously in a DaemonThread"""
    Thread(target=func, daemon=True).start()


noop = lambda *x: None


def not_raising(func):
    """Wraps a function and swallows exceptions.

    Args:
        func: function to wrap

    Returns:
        wrapped function, that does not raise Exceptions,
        Exceptions are printed to console
    """

    def logging_func(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except:
            traceback.print_exc()

    return logging_func


def on_change(file, callback, delay=1, forking=1):
    t = getmtime(file)

    def check():
        while True:
            if getmtime(file) != t:
                callback()
            sleep(delay)

    if forking:
        fork(check)
    else:
        check()


_cleanup = 0


def cleanup_at_exit(gpio):
    global _cleanup
    if not _cleanup:
        atexit.register(gpio.cleanup)
        _cleanup = 1


class IRQHandler:
    """Abstraction of an IRQ handler.

    An edge on the IRQ pin sets a flag.  The callback is invoked on a separate
    thread when the flag was set.  The flag is reset when the pin is high again.
    The callback may be invoked repeatedly if the pin does not reset. So you have
    to reset the IRQ inside the callback, such that when the callback returns,
    the IRQ line is high again.

    This uses RPi.GPIO_ internally.

    .. _RPi.GPIO: https://pypi.python.org/pypi/RPi.GPIO
    .. _BCM: https://pinout.xyz/

    Args:
        pin (int): BCM_ pin number attached to IRQ line. 0 disables use of GPIO
            pins, call ``interrupt`` explicitly
        callback: function invoked on IRQ.
        edge (int): fire interrupt on falling=0 or rising=1 edge. 1 inverts
            the logic, so IRQ is considered reset when low.
        pullup (int): activate internal pullup
            1=pullup, 0=nothing, -1=pulldown.
    """

    def __init__(self, pin, callback, edge=0, pullup=1):
        if pin:
            GPIO.setmode(GPIO.BCM)
            cleanup_at_exit(GPIO)
            pud = [GPIO.PUD_DOWN, GPIO.PUD_OFF, GPIO.PUD_UP][pullup + 1]
            reset = GPIO.LOW if edge else GPIO.HIGH
            edge = GPIO.RISING if edge else GPIO.FALLING
            GPIO.setup(pin, GPIO.IN, pull_up_down=pud)
            GPIO.add_event_detect(pin, edge, self.interrupt)

            def is_reset(): return GPIO.input(pin) == reset
        else:
            def is_reset(): return True

        self._irq = Event()
        callback = not_raising(callback)

        def loop():
            while True:
                self._irq.wait()
                callback()
                if is_reset():
                    self._irq.clear()

        fork(loop)

    def interrupt(self, *a, **kw):
        """fire interrupt

        All arguments are ignored.
        """
        self._irq.set()


class Poller:
    """Polling loop as replacement for IRQHandler.

    Use it if using the IRQ line is not possible or desired.

    Args:
        callcack: function that is called continously. The actuall polling
            happens in this callback.
        delay (float): delay in seconds between invocations of callback
    """

    def __init__(self, callback, delay=0.01):

        callback = not_raising(callback)

        def loop():
            while True:
                callback()
                sleep(delay)

        fork(loop)


class Polling:
    """universal halting Polling loop

    The loop halts if the state did not change for the given number of polls
    """

    def __init__(self, getter, setter, delay=0.01, count=100):
        event = Event()

        def poll():
            k = -1
            state=None
            while True:
                if count and k < 0:
                    event.clear()
                    event.wait()
                    k = count
                s=getter()
                setter(s)
                if state!=s:
                    k = count
                else:
                    k -= 1
                state=s
                sleep(delay)

        fork(poll)

        return event.set
