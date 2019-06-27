#!/usr/bin/env python
# -*- coding: utf-8 -*-

def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton


@singleton
class Car():
    def __init__(self):
        pass


def main():
    car = Car()
    print id(car)
    car = Car()
    print id(car)
    car = Car()
    print id(car)

if __name__ == '__main__':
    main()