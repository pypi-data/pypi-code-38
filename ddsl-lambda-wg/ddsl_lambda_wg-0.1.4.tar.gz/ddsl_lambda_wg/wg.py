import queue
import time
import threading
from ddsl_lambda_wg.timer import *

import numpy as np
def get_random_wait_time(rps):
    scale = 1/rps
    return np.random.exponential(scale)

class WorkerThread(threading.Thread):
    def __init__(self, parent, sleep_time=2):
        super(WorkerThread, self).__init__()
        # if daemon is true this thread will die when the main thread dies
        self.daemon = True
        self.stop_signal = False
        self.parent = parent

    def run(self):
        while not self.stop_signal:
            try:
                item = self.parent.q.get(timeout=1)
                # print('-', end='')
                if item is None:
                    time.sleep(.01)
                    continue
                else:
                    res = self.parent.worker_func()
                    self.parent.temp_stats.append(res)
            except queue.Empty:
                time.sleep(.01)
                continue

class DdslLambdaWG:
    def __init__(self, worker_func, rps=10/60, worker_thread_count=10, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rps = rps
        self.worker_threads = None
        self.temp_stats = []
        self.worker_thread_count = worker_thread_count
        self.worker_func = worker_func
        self.q = queue.Queue()

    def get_stats(self):
        return self.temp_stats

    def fire(self):
        self.q.put(1)

    def reset_stats(self):
        self.temp_stats = []
        return True
    
    def set_rps(self, new_rps):
        self.rps = new_rps
        return True

    def prepare_test(self):
        self.fire_timer = TimerClass()
        self.fire_timer.tic()

    def fire_wait(self):
        wait_time = get_random_wait_time(self.rps) - self.fire_timer.toc()
        if wait_time > 0:
            time.sleep(wait_time)

        self.fire_timer.tic()
        self.fire()

    def stop_workers(self):
        if self.worker_threads is not None:
            for worker_thread in self.worker_threads:
                worker_thread.stop_signal = True
            return True
        else:
            return True

    def __del__(self):
        self.stop_workers()

    def start_workers(self):
        self.stop_workers()
        self.worker_threads = []
        for i in range(self.worker_thread_count):
            worker_thread = WorkerThread(self)
            worker_thread.start()
            self.worker_threads.append(worker_thread)

