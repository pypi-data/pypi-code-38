# -*- coding: utf-8 -*-
__author__ = '陈章'
__date__ = '2019-05-13 17:12'
import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed


class Parallel:
    @classmethod
    def run_func_parallel(cls, func, func_args_list, callback_func, callback_func_extra_kwargs, style="thread",
                          max_workers=os.cpu_count()):
        """
        :param func: only support function, not method
        :param func_args_list:
        :param callback_func: only support function, not method
        :param style:
        :param max_workers:
        :return:
        """
        if style == 'thread':
            executor = ThreadPoolExecutor(max_workers=max_workers)
        elif style == "process":
            executor = ProcessPoolExecutor(max_workers=max_workers)
        else:
            raise Exception("argument style invalid, please pass thread or process")
        tasks = []
        for func_arg in func_args_list:
            if not isinstance(func_arg, list) and not isinstance(func_arg, tuple):
                func_arg = [func_arg]
            tasks.append(executor.submit(func, *func_arg))
        i = 0
        for r in as_completed(tasks):
            i += 1
            callback_func(i, r.result(), callback_func_extra_kwargs)


run_func_parallel = Parallel.run_func_parallel
