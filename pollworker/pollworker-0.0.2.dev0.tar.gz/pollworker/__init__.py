# coding=utf8

from pollworker.processes import LogicHolder, PollerHolder, master_process
from multiprocessing import cpu_count


def regist_worker(func):
    """
    regist a function with message parameter to process the message from master process
    :param func: function with message parameter
    :return:
    """
    LogicHolder.instance().regist(func)


def regist_poller(obj):
    """
    regist a poll object that contains poll method with queue name parameter
    :param obj: Object with poll method
    :return:
    """
    PollerHolder.instance().regist(obj)


def start(workers=0, stopwaits=0):
    if workers < 1:
        _cpus = cpu_count()
        workers = _cpus - 1 if _cpus > 1 else 1
    master_process(workers, stopwaits)
