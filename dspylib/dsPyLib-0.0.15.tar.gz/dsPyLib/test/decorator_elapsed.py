# -*-coding:utf-8-*-
__author__ = 'Dragon Sun'


from dsPyLib.utils.decorator import *


@elapsed
def func():
    time.sleep(1.0)


if __name__ == '__main__':
    func()
