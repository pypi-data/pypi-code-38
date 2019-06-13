# -*-coding:utf-8-*-
__author__ = 'Dragon Sun'


from dsPyLib.utils.decorator import *


@timer()
def func1():
    print('1')


@timer(2)
def func2():
    print('2')


@timer(3, 4)
def func3():
    print('3')


if __name__ == '__main__':
    func1()
    func2()
    func3()
    print('Complete')
