# -*- coding:utf-8 -*-

from datetime import datetime, timedelta
from time import sleep

__all__ = ['RetryTimer']


class RetryTimer(object):
    def __init__(self, max_wait=None, interval=None):
        self.max_wait = max_wait
        self.interval = interval

        self.next_interval = 0.0
        self.start_time = None

    def retry(self):
        if self.start_time is None:
            self.start_time = datetime.now()

        sleep(self.next_interval)
        if self.interval is not None:
            self.next_interval = self.interval
        return self.check()

    def check(self):
        if self.max_wait is None:
            return True

        if self.start_time is None:
            return True
        elif self.start_time + timedelta(seconds=self.max_wait) >= datetime.now():
            return True
        else:
            return False
