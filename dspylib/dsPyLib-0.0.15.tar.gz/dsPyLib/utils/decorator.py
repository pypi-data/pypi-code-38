# -*-coding:utf-8-*-
__author__ = 'Dragon Sun'


import time
import threading
from functools import wraps
from dsPyLib.utils.datetime import *
from dsPyLib.utils.scheduler import Scheduler


"""
    计算函数运行时间的修饰器
    使用方法：
        from dsPyLib.utils.decorator import *
        
        @elapsed
        def func():w
"""


def elapsed(callback):
    """
    获取函数执行时间
    :param callback:
    :return:
    """
    @wraps(callback)
    def wrapper(*args, **kwargs):
        # 记录下开始时间
        start = time.perf_counter()

        # 执行函数
        result = callback(*args, **kwargs)

        # 计算消耗时间
        elapse = time.perf_counter() - start

        # 输出信息
        func_file = callback.__code__.co_filename
        func_line = callback.__code__.co_firstlineno
        func_name = callback.__code__.co_name
        print(f'{func_file}, {func_line}, {func_name}() elapsed time: {elapse} seconds.')

        return result
    return wrapper


"""
    定时执行方法的修饰器
    使用方法：
        from dsPyLib.utils.decorator import *
        
        # interval 每隔多少秒执行(默认1); count 一共执行多少次(默认None，即不限次数)
        @timer(interval, count)     
        def func():
"""


def timer(interval=1, count=None):
    def _timer(callback):
        @wraps(callback)
        def wrapper(*args, **kwargs):
            def run():
                loop = 0
                while (not count) or (count and (loop < count)):
                    loop += 1
                    callback(*args, **kwargs)
                    if count and (loop >= count):
                        break
                    time.sleep(interval)

            thread = threading.Thread(target=run)
            thread.start()
        return wrapper
    return _timer


"""
    计划执行方法的修饰器
    使用方法：
        from dsPyLib.utils.decorator import *

        @schedule(start='2018-08-17 17:08:12', wp=True, loop=3, interval=1, unit=CycleUnit.minute)
        def func(s1, s2):
            print(s1, s2)

        if __name__ == '__main__':
            func('1', '2')
"""


def schedule(start=None, wp=False, loop=None, interval=1, unit=CycleUnit.day):
    """
    计划执行

    :param start: str/datetime，开始时间
        1. None，则采用当前时间
        2. str，则用"%Y-%m-%d %H:%M:%S"转化为时间
        3. datetime
        最后与当前时间取最大值。也就是说，这个值应该设置为一个未来的时间，否则按当前时间处理
    :param wp: boolean, 是否整点触发
    :param loop: int, 执行的次数，如果为None则不限次数
    :param interval: int, 周期的间隔次数
    :param unit: CycleUnit, 周期单位
    :return: 无

    示例：
        @schedule(start='2018-08-17 17:08:12', wp=True, loop=3, interval=1, unit=CycleUnit.minute)
        表示：
            如果'2018-08-17 17:08:12'大于当前时间，则从'2018-08-17 17:09:00'开始，每隔1分钟执行一次，共执行3次
            如果'2018-08-17 17:08:12'小于当前时间，则从当前时间的下一个整分开始，每隔1分钟执行一次，共执行3次
    """
    def _timer(callback):
        @wraps(callback)
        def wrapper(*args, **kwargs):
            s = Scheduler()
            if type(start) is str:
                start_time = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
            else:
                start_time = start
            dt = max(datetime.datetime.now(), start_time) if start else datetime.datetime.now()
            if wp:
                dt = whole_point(dt, unit)
                dt = next_time(dt, 1, unit)
            s.add_job(dt, loop, interval, unit, callback, *args, **kwargs)
            s.start()
        return wrapper
    return _timer
