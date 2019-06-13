# -*-coding:utf-8-*-
__author__ = 'Dragon Sun'


from dsPyLib.utils.decorator import *


@schedule(start='2018-08-17 17:08:12', wp=True, loop=3, interval=1, unit=CycleUnit.minute)
def func1(s1, s2):
    print('func1', s1, s2)


@schedule(interval=2, unit=CycleUnit.second)
def func2():
    print('func2')


if __name__ == '__main__':
    func1('1', '2')
    func2()
    print('xx')
