import time

from swissarmykit.utils.loggerutils import LoggerUtils
from swissarmykit.lib.core import Singleton

try: from definitions_prod import *
except Exception as e: pass # Surpass error. Note: Create definitions_prod.py

class Timer:

    def __init__(self, total=0, file_name='/timer_'):
        self.log = LoggerUtils(appConfig.LOG_PATH + file_name) # type: LoggerUtils
        self.log.info('Total: %d' % total)
        self.t0 = time.time()
        self.total_task = total
        self.remain_task = total

    def reset(self, total=0):
        self.t0 = time.time()
        self.total_task = total
        self.remain_task = total

    def check(self):
        self.remain_task -= 1
        # print('.', end='', flush=True)

        if self.remain_task % 1000 == 0:
            t1 = time.time()
            time_spent = (t1 - self.t0) / 60

            if self.total_task:
                done_task = self.total_task - self.remain_task

                self.log.info("ETA: {}m. Elapsed time: {}m. Remain: {} tasks.".format(
                    round(self.remain_task * time_spent / done_task, 2), round(time_spent, 2), self.remain_task))
            else:
                self.log.info("Elapsed time: {}m. Total: {} tasks.".format(round(time_spent, 2), abs(self.remain_task)))

    def done(self):
        self.spent()

    def spent(self):
        t1 = time.time()
        time_spent = (t1 - self.t0) / 60
        self.log.info("Elapsed time: {}m.".format(round(time_spent, 2)))

if __name__ == '__main__':
    timer = Timer()
    for i in range(2001):
        timer.check()
