# -*- coding: utf-8 -*-

from schedule import Scheduler as Sched


class SchedulerException(Exception):
    def __init__(self, info):
        super().__init__(self)
        self._info = info

    def __str__(self):
        return self._info


class Scheduler(object):
    def __init__(self, config):
        self._debug = config['debug']
        self._interval = config.get('interval', 10)
        self._sched = Sched()

    def add(self, func, args, tag):
        if self._sched is None:
            raise SchedulerException('required to create scheduler')
        self._sched.every(self._interval).seconds.do(func, args=args).tag(tag)

    def run(self):
        if self._sched is None:
            raise SchedulerException('required to create scheduler')
        self._sched.run_pending()

    def stop(self, tag=None):
        if self._sched is None:
            raise SchedulerException('required to create scheduler')
        self._sched.clear(tag)
