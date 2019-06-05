#coding:utf-8
from __future__ import (print_function, unicode_literals)
import time
try:
    import wx
except:
    try:
        import PyQt5
    except:
        pass

def wrapper_call_after(func):
    def _wrapper(*args, **kwargs):
        return wx.CallAfter(func, *args, **kwargs)
    return _wrapper

#TODO
def wr_prog_exec_time_out(elapse=None):

    def wrapper_prog_exec_time(func):
        """
        包含了其他程序使用CPU的时间，是程序开始到程序结束的运行时间。
        :param func:
        :return:
        """
        if elapse is None:
            elapse = []
        def _wrapper(*args, **kwargs):
            start = time.time()
            ret = func(*args, **kwargs)
            end = time.time()
            return end - start, ret
        return _wrapper
    return wrapper_prog_exec_time

def wrapper_prog_exec_time(func):
    """
    包含了其他程序使用CPU的时间，是程序开始到程序结束的运行时间。
    :param func:
    :return:
    """

    def _wrapper(*args, **kwargs):
        start = time.time()
        ret = func(*args, **kwargs)
        end = time.time()
        return end - start
    return _wrapper


def wrapper_cpu_exec_time(func):
    """
    只计算了程序运行的CPU时间，相对准确
    :param func:
    :return:
    """
    def wrapper(*args, **kwargs):
        start = time.clock()  
        func(*args, **kwargs)
        end =time.clock()
        print('used:', end - start)
        return end - start
    return wrapper

def wrapper_round_n_float(radix):
    def _wrapper(fun):
        def return_fun(*args, **kwargs):
            ret = fun(*args, **kwargs)
            return round(ret, radix)
        return return_fun
    return _wrapper

def wrapper_print_args(func):
    def _wrapper(*args, **kwargs):
        print("Arguments were: %s, %s" % (args, kwargs))
        ret = func(*args, **kwargs)
        return ret
    return _wrapper


def singleton(cls):
    import functools
    instance={}
    @functools.wraps(cls)
    def _singleton(*args, **kw):
        if cls not in instance:
            instance[cls]=cls(*args, **kw)
        return instance[cls]
    return _singleton

if __name__ == "__main__":
    pass