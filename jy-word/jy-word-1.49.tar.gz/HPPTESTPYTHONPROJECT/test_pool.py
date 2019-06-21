# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2018/7/10 0010
__author__ = 'huohuo'

import time
import multiprocessing


def write_file(filename,num):
    target = open(filename, 'w')
    for i in range(1,num+1):
        target.write("%d line\n" % i)

if __name__ == '__main__':
    # start = time.time()
    #
    # p1 = multiprocessing.Process(target=write_file,args=('1.txt', 1000000))
    # p2 = multiprocessing.Process(target=write_file,args=('2.txt', 2000000))
    #
    # #启动子进程
    # p1.start()
    # p2.start()
    #
    # #等待fork的子进程终止再继续往下执行，可选填一个timeout参数
    # p1.join()
    # p2.join()
    #
    # end = time.time()
    # print str(round(end-start,3))+'s'

    start = time.time()
    #100W
    write_file('1.txt', 1000000)
    #200W
    write_file('2.txt', 2000000)

    end = time.time()
    print str(round(end-start,3))+'s'
