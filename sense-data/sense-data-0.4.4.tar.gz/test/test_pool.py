#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Copyright (C)2018 SenseDeal AI, Inc. All Rights Reserved
File: {name}.py
Author: xuwei
Email: weix@sensedeal.ai
Last modified: 2018.12.23
Description:
'''

from multiprocessing import *
from sense_data import *

# 多进程执行函数
def test(i):
    print(get_stock_price_day(i))

#多进程管理函数
def pool_process(functor,list,num):
    pass
    pool = Pool(num)
    pool.map(functor, list) #functor 是计算函数，list是列表
    pool.close()  # 关闭进程池，不再接受新的进程
    pool.join()  # 主进程阻塞等待子进程的退出

# 分配
def loop():
    l = [str(i) for i in range(1000)]
    pool_process(test,l ,4)

if __name__ == '__main__':
    loop()