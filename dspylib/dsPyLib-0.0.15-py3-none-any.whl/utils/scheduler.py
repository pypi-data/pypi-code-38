# -*-coding:utf-8-*-
__author__ = 'Dragon Sun'


import copy
import time
import threading
from dsPyLib.utils.datetime import *


"""
    从dt开始，每interval个unit执行一次，执行loop次后结束，如果loop为None，则无限次执行下去
    
    示例：
        from dsPyLib.utils.scheduler import *
        
        def func(s1, s2):
            print(s1, s2)        
        
        if __name__ == '__main__':
            scheduler = Scheduler()
            scheduler.add_job(datetime.datetime.now(), None, 3, CycleUnit.second, func, 'aa', 'bb')
            scheduler.start()
            print('XX')
"""


class Scheduler(object):
    sleep_interval = 1.0

    def __init__(self):
        self.jobs = list()
        self.thread = threading.Thread(target=self._work)

    def start(self):
        self.thread.start()

    def add_job(self, dt=None, loop=None, interval=1, unit=CycleUnit.minute,
                callback=None, *args, **kwargs):
        job = {
            'dt': dt,
            'loop': loop,
            'cur_loop': 0,
            'interval': interval,
            'unit': unit,
            'callback': callback,
            'args': args,
            'kwargs': kwargs
        }
        self.jobs.append(job)

    def _add_next_job(self, job):
        next_job = copy.deepcopy(job)
        next_job['dt'] = next_time(next_job['dt'], next_job['interval'], next_job['unit'])
        next_job['cur_loop'] += 1
        if (next_job['loop'] is None) or (next_job['loop'] > next_job['cur_loop']):
            self.jobs.append(next_job)

    def _work(self):
        while len(self.jobs) > 0:
            for job in self.jobs:
                if job['dt'] and (datetime.datetime.now() > job['dt']):
                    self._add_next_job(job)
                    self.jobs.remove(job)
                    if job['callback']:
                        job['callback'](*job['args'], **job['kwargs'])
            time.sleep(0.5)
