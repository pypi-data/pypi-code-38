#!/usr/bin/env python

from j5basic import Timer
from j5test import Utils
import virtualtime
from virtualtime import test_virtualtime
import threading
import time

class TimerDriver:
    def __init__(self, expecteddiff=1, expectarg=False):
        self.lasttime = None
        self.expecteddiff = expecteddiff
        self.expectarg = expectarg
        self.ticks = 0
        self.errors = []

    def timefunc(self, testarg=None):
        tm = time.time()
        self.ticks += 1
        assert not self.expectarg or testarg is not None
        if self.lasttime != None:
            actual_diff = tm - self.lasttime
            if abs(actual_diff - self.expecteddiff) > (float(self.expecteddiff) / 10):
                self.errors.append("timefunc started at %r was %r later than last time %r" % (tm, actual_diff, self.lasttime))
                print(self.errors[-1])
        self.lasttime = tm

    def sleepfunc(self, testarg=None):
        """takes an iterable and sleeps for item seconds for each item"""
        next_sleep = next(testarg)
        tm = time.time()
        self.lasttime = tm
        self.ticks += 1
        print(tm, next_sleep, self.ticks)
        if next_sleep:
            time.sleep(next_sleep)

class TestTimer(object):
    def sleep(self, seconds):
        """An overridable method to call time.sleep"""
        time.sleep(seconds)

    def finish_wait(self, thread, error_list, expected_sleep=0):
        """Waits for the thread to finish, checks for any errors in the given list. expected_sleep says how long we should have to wait for this..."""
        thread.join()
        assert not error_list

    @Utils.if_long_test_run()
    def test_onesec(self):
        """Test the one second resolution"""
        tm = TimerDriver()
        timer = Timer.Timer(tm.timefunc)
        thread = threading.Thread(target=timer.start)
        thread.start()
        self.sleep(3)
        timer.stop = True
        assert tm.lasttime is not None
        assert 2 <= tm.ticks <= 3
        self.finish_wait(thread, tm.errors)

    @Utils.if_long_test_run()
    def test_twosec(self):
        """Test a non one second resolution"""
        tm = TimerDriver(2)
        timer = Timer.Timer(tm.timefunc, resolution=2)
        thread = threading.Thread(target=timer.start)
        thread.start()
        self.sleep(5)
        timer.stop = True
        assert tm.lasttime is not None
        assert 2 <= tm.ticks <= 3
        self.finish_wait(thread, tm.errors)

    @Utils.if_long_test_run()
    def test_args(self):
        """Test passing args"""
        tm = TimerDriver(expectarg=True)
        timer = Timer.Timer(tm.timefunc, args=(True,))
        thread = threading.Thread(target=timer.start)
        thread.start()
        self.sleep(3)
        timer.stop = True
        assert tm.lasttime is not None
        self.finish_wait(thread, tm.errors)

    @Utils.if_long_test_run()
    def test_missed(self):
        """Test missing time events by sleeping in the target function"""
        tm = TimerDriver(1)
        timer = Timer.Timer(tm.sleepfunc, args=(iter([0,2,3,0,6]),))
        thread = threading.Thread(target=timer.start)
        thread.start()
        start_time = virtualtime._original_time()
        # make sure our sleep happens within the last 6-second pause
        self.sleep(12)
        print(time.time(), tm.lasttime)
        timer.stop = True
        assert tm.lasttime is not None
        assert 4 <= tm.ticks <= 5
        self.finish_wait(thread, tm.errors, 6)

    @Utils.if_long_test_run()
    def test_kwargs(self):
        """Test passing kwargs"""
        tm = TimerDriver(expectarg=True)
        timer = Timer.Timer(tm.timefunc, kwargs={"testarg":True})
        thread = threading.Thread(target=timer.start)
        thread.start()
        self.sleep(3)
        timer.stop = True
        assert tm.lasttime is not None
        self.finish_wait(thread, tm.errors)

    def test_short_run(self):
        """Test stopping immediately"""
        tm = TimerDriver(expectarg=True)
        timer = Timer.Timer(tm.timefunc, kwargs={"testarg":True}, resolution=10)
        thread = threading.Thread(target=timer.start)
        thread.start()
        timer.stop = True
        assert tm.lasttime is None
        self.finish_wait(thread, tm.errors)

class TestVirtualTimer(TestTimer, test_virtualtime.RunPatched):
    """Tests that Timers react appropriately to virtual time setting"""
    def sleep(self, seconds):
        virtualtime.fast_forward_time(seconds)

    def finish_wait(self, thread, error_list, expected_sleep=0):
        """Waits for the thread to finish, checks for any errors in the given list. expected_sleep says how long we should have to wait for this..."""
        if expected_sleep:
            virtualtime.fast_forward_time(expected_sleep)
        super(TestVirtualTimer, self).finish_wait(thread, error_list, expected_sleep)

