#!/usr/bin/env python

from j5basic import TimedLock
try:
    from j5.OS import ThreadControl
except ImportError:
    ThreadControl = None
from j5test import Utils
import threading
import time

def simple_acquire_release(lock):
    """simple acquire and release of object from one thread"""
    lock.acquire()
    lock.release()

def reentrant_acquire_release(lock):
    """multiple acquire and release of object from one thread, to test it being reentrant"""
    lock.acquire()
    lock.acquire()
    lock.acquire()
    lock.release()
    lock.release()
    lock.acquire()
    lock.release()
    lock.release()

def schedule_acquire_release(lock, t1, t2, t3, ea=None, er=None):
    """simple acquire and release of object from one thread, with pauses and notification on acquire and release (sets er if fails to acquire) - events receive timestamps too"""
    name = threading.currentThread().getName()
    start_time = time.time()
    def elapsed_time():
        return "%0.3f" % (time.time() - start_time)
    print(elapsed_time(), name, "sleep", t1)
    time.sleep(t1)
    print(elapsed_time(),  name, "acquire", t2)
    if lock.acquire(t2):
        if ea:
            ea.ts = time.time()
            print(elapsed_time(),  name, "acquired", ea.ts)
            ea.set()
        else:
            print(elapsed_time(),  name, "acquired")
        print(elapsed_time(),  name, "sleep", t3)
        time.sleep(t3)
        print(elapsed_time(),  name, "release")
        lock.release()
    if er:
        er.ts = time.time()
        print(elapsed_time(),  name, "finished", er.ts)
        er.set()
    else:
        print(elapsed_time(),  name, "finished")

class TestTimedLock(object):
    def ensure_stopped(self, *threads):
        threads_stopped = []
        for thread in threads:
            if thread.isAlive():
                threads_stopped.append(str(thread))
                if ThreadControl:
                    ThreadControl.stop_thread(thread)
        if threads_stopped:
            raise ValueError("Threads %s did not release lock in expected time", ", ".join(threads_stopped))

    def test_simple(self):
        """tests that the locks basically work in a single thread"""
        lock = TimedLock.TimedLock()
        bt = threading.Thread(target=simple_acquire_release, name="bt", args=(lock,))
        bt.start()
        time.sleep(0.01)
        self.ensure_stopped(bt)

    def test_simple_reentrant(self):
        """tests that the locks are reentrant"""
        lock = TimedLock.TimedLock()
        bt = threading.Thread(target=reentrant_acquire_release, name="bt", args=(lock,))
        bt.start()
        time.sleep(0.01)
        self.ensure_stopped(bt)

    def test_wait_timeout(self):
        """tests that the acquire with a wait parameter actually times out and fails to acquire if it's still locked"""
        lock = TimedLock.TimedLock()
        bt1_ea, bt1_er, bt2_ea, bt2_er = threading.Event(), threading.Event(), threading.Event(), threading.Event()
        bt1 = threading.Thread(target=schedule_acquire_release, name="bt1", args=(lock, 0, None, 0.3), kwargs=dict(ea=bt1_ea, er=bt1_er))
        bt2 = threading.Thread(target=schedule_acquire_release, name="bt2", args=(lock, 0.1, 0.1, 0.1), kwargs=dict(ea=bt2_ea, er=bt2_er))
        bt2.start()
        bt1.start()
        bt1_er.wait(1)
        bt2_er.wait(1)
        self.ensure_stopped(bt1)
        self.ensure_stopped(bt2)
        assert bt1_ea.isSet()
        assert bt1_er.isSet()
        assert not bt2_ea.isSet()
        assert bt2_er.isSet()

    def test_wait_success(self):
        """tests that the acquire with a wait parameter actually acquires the lock and doesn't wait the expected period of time"""
        lock = TimedLock.TimedLock()
        bt1_ea, bt1_er, bt2_ea, bt2_er = threading.Event(), threading.Event(), threading.Event(), threading.Event()
        bt1 = threading.Thread(target=schedule_acquire_release, name="bt1", args=(lock, 0, None, 0.1), kwargs=dict(ea=bt1_ea, er=bt1_er))
        bt2 = threading.Thread(target=schedule_acquire_release, name="bt2", args=(lock, 0.1, 1.0, 0), kwargs=dict(ea=bt2_ea, er=bt2_er))
        bt2.start()
        bt1.start()
        bt1_er.wait(0.2)
        bt2_er.wait(1.2)
        self.ensure_stopped(bt1)
        self.ensure_stopped(bt2)
        assert bt1_ea.isSet()
        assert bt1_er.isSet()
        assert bt2_ea.isSet()
        assert bt2_er.isSet()
        # check that we didn't wait very long to catch the event
        print("delay time", bt2_ea.ts - bt1_er.ts)
        assert bt2_ea.ts - bt1_er.ts < 0.1

    @Utils.if_long_test_run()
    def test_wait_multi(self):
        """tests that the acquire with a wait parameter actually works with multiple threads"""
        lock = TimedLock.TimedLock()
        thread_count = 30
        bt_ea = [threading.Event() for i in range(thread_count)]
        bt_er = [threading.Event() for i in range(thread_count)]
        bt = [threading.Thread(target=schedule_acquire_release, name="bt%d" % i, args=(lock, 0.01*i, 1*thread_count*2, 0.01), kwargs=dict(ea=bt_ea[i], er=bt_er[i])) for i in range(thread_count)]
        start_time = time.time()
        [bt_n.start() for bt_n in bt]
        [e.wait(1*thread_count*3) for e in bt_er]
        wait_complete_time = time.time()
        print("wait completed at %0.2f" % time.time())
        # allow a short amount of time for threads to exit after setting the event
        time.sleep(0.01)
        self.ensure_stopped(*bt)
        def elapsed_time(e):
            ts = getattr(e, "ts", None)
            return ts - start_time if ts else None
        print("n, acquired, ts, released, ts")
        for i in range(thread_count):
            print(i, bt_ea[i].isSet(), elapsed_time(bt_ea[i]), bt_er[i].isSet(), elapsed_time(bt_er[i]))
        for i in range(thread_count):
            print(i)
            assert bt_ea[i].isSet()
            assert bt_er[i].isSet()
        # check that we didn't wait very long to catch the event
        final_er = max(bt_er_n.ts for bt_er_n in bt_er)
        first_ea = min(bt_ea_n.ts for bt_ea_n in bt_ea)
        print("elapsed time", final_er - first_ea)
        assert final_er - first_ea < 0.03*thread_count*3

    @Utils.if_long_test_run()
    def test_wait_blocking_success(self):
        """tests that the acquire with a wait parameter of True actually acquires the lock and doesn't wait the expected period of time"""
        lock = TimedLock.TimedLock()
        bt1_ea, bt1_er, bt2_ea, bt2_er = threading.Event(), threading.Event(), threading.Event(), threading.Event()
        bt1 = threading.Thread(target=schedule_acquire_release, name="bt1", args=(lock, 0, None, 1.1), kwargs=dict(ea=bt1_ea, er=bt1_er))
        bt2 = threading.Thread(target=schedule_acquire_release, name="bt2", args=(lock, 0.1, True, 0), kwargs=dict(ea=bt2_ea, er=bt2_er))
        bt2.start()
        bt1.start()
        bt1_er.wait(0.2)
        # we test waiting for more than a second because True == 1
        bt2_er.wait(2.2)
        self.ensure_stopped(bt1)
        self.ensure_stopped(bt2)
        assert bt1_ea.isSet()
        assert bt1_er.isSet()
        assert bt2_ea.isSet()
        assert bt2_er.isSet()
        # check that we didn't wait very long to catch the event
        assert bt2_ea.ts - bt1_er.ts < 1.11

