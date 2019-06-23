#!/usr/bin/env python
# encoding: utf-8
"""
@author: 熊利宏
@email:xionglihong@163.com
@phone：15172383635
@project: xToolkit
@file: 多线程逻辑模块
@time: 2019-05-31 下午3:07
"""

import threading


class MyThreading(threading.Thread):
    def __init__(self, func, args):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args

    def run(self):
        if self.args:
            self.res = self.func(self.args)
        else:
            self.res = self.func()

    def getResult(self):
        return self.res


def xthreading(funcs, args=None):
    nfuncs = range(len(funcs))

    if not args:
        args = {}
        for key in funcs:
            args.update({key.__name__: []})

    result = []  # 存放返回结果
    threads = []  # 存放多线程对象
    for i in nfuncs:
        t = MyThreading(funcs[i], args[funcs[i].__name__])
        threads.append(t)

    for i in nfuncs:
        threads[i].start()

    for i in nfuncs:
        threads[i].join()
        result.append({funcs[i].__name__: threads[i].getResult()})

    return result
