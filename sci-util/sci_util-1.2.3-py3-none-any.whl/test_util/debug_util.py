#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: violinsolo
# Created on 2019/3/8


import time


# ======
# test seconds process time (wall time or CPU time) meets
# ======
def test_time_meets(seconds):
    def wrapper(func):
        def _wrapper(*args, **kwargs):
            start = time.process_time()
            func(*args, **kwargs)
            end = time.process_time()
            if end - start > seconds:
                print('bad!')
            else:
                print('good!')

        return _wrapper

    return wrapper


# ======
# print fn running seconds process time (wall time or CPU time)
# ======
def test_time_costs(func):
    # print(func.__name__)
    def _wrapper(*args, **kwargs):
        start = time.process_time()
        fn_res = func(*args, **kwargs)
        end = time.process_time()

        print(f'fn:"{func.__name__}" costs {round(end - start, 5)} seconds')
        return fn_res

    return _wrapper


if __name__ == '__main__':

    # ========
    # test time set
    @test_time_meets(1)
    def myfunc(*args, **kwargs):
        for i in range(100000000):
            pass

    myfunc()


    # ========
    # test time costs
    @test_time_costs
    def myfunc2(*args, **kwargs):
        x = 0
        for i in range(100000):
            x += i
        return x

    m = myfunc2()
    print(m)