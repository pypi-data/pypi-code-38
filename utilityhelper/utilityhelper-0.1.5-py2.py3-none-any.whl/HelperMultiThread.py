#-*- coding:utf-8 -*-
'''
helper.HelperMultiThread
~~~~~~~~~~~~~~~~~~~~~~~~~
对threading模块封装；
多线程操作

Created on 2016年7月8日

@author: 龚磊磊
'''
from __future__ import (print_function, unicode_literals)
import threading

class WorkerThread(threading.Thread):
    '''通过继承threading.Thread类，重写父类的run方法的方式创建一个线程
    '''
    def __init__(self, work=None, callback=None, *args, **kwargs):
        '''调用父类的初始化方法初始化一个线程
        
        @param work: 执行的任务，函数或可执行对象
        @param callback: 执行任务后，回调的处理函数
        
        '''
        super(WorkerThread, self).__init__()
        self.work = work
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.setDaemon(True)
        self.__stopevent = threading.Event()

    def run(self):
        self.__stopevent.clear()
        ret = self.work(*self.args, **self.kwargs)
        if self.callback:
            self.callback(*ret)
        
    def stop(self):
        self.__stopevent.set()

if __name__ == '__main__':
    pass