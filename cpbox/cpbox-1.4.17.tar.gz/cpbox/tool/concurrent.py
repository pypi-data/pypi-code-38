# coding: utf-8
import sys
is_py2 = sys.version[0] == '2'
if is_py2:
    from Queue import Queue
else:
    from queue import Queue
from threading import Timer, Lock, Thread

import copy
from cpbox.tool import array
from cpbox.tool import utils
import logging
import time
logger = logging.getLogger()

debug_concurrent = False

def waiting(get_fn, check_should_wait_fn, on_waiting_fn, interval=5, wait_before_start=0):
    if wait_before_start:
        time.sleep(wait_before_start)
    while True:
        ret = get_fn()
        should_wait = check_should_wait_fn(ret)
        if should_wait:
            if callable(on_waiting_fn):
                on_waiting_fn(ret)
            time.sleep(interval)
        else:
            return ret

class Worker(object):
    def __init__(self, num_worker_threads = 2):
        self.queue = Queue()
        for i in range(num_worker_threads):
            t = Thread(target=self.do_work)
            t.daemon = True
            t.start()

    def do_work(self):
        if debug_concurrent:
            logger.debug('begin_do_work')
        while True:
            callback, data = self.queue.get()
            callback(data)
            self.queue.task_done()

    def submit(self, callback, data):
        self.queue.put((callback, data))

    def wait(self):
        self.queue.join()

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.daemon = True
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

class DelayOp:

    def __init__(self, callback, timeout = 3, threshold = 10):
        self.callback = callback
        self.timeout = timeout
        self.threshold = threshold
        self.data_list = []
        self.lock = Lock()
        self.skip_timer_check_for_one_round = False
        self.timer = RepeatedTimer(self.timeout, self._do_timer_check)
        self.worker = Worker(4)

    def _do_timer_check(self):
        if debug_concurrent:
            logger.debug('_do_timer_check')
        if self.skip_timer_check_for_one_round:
            self.skip_timer_check_for_one_round = False
            if debug_concurrent:
                logger.debug('_do_timer_check skipped')
            return
        self.lock.acquire()
        self._do_check(True)
        self.lock.release()

    def _do_check(self, skip_threshold_check_for_timer = False):
        if debug_concurrent:
            logger.debug('_do_check')
        size = len(self.data_list)
        reach_threshold = size >= self.threshold
        if reach_threshold:
            self.skip_timer_check_for_one_round = True
        if reach_threshold or (size > 0 and skip_threshold_check_for_timer):
            list = copy.deepcopy(self.data_list)
            self.data_list = []
            for sub_list in array.chunks(list, self.threshold):
                self.worker.submit(self.callback, sub_list)

    def add_delay_item(self, item):
        if debug_concurrent:
            logger.debug('add_delay_item: %s', item)
        self.lock.acquire()
        self.data_list.append(item)
        self._do_check(False)
        self.lock.release()
