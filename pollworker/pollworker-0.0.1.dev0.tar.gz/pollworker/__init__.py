# coding=utf8

from pollworker.processes import LogicHolder, PollerHolder, master_process
from multiprocessing import cpu_count

_cpus = cpu_count()

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


def start(queue_name, workers=_cpus, stopwaits=0):
    master_process(queue_name, workers, stopwaits)
