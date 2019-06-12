#!/usr/bin/env python

"""Singleton metaclass implementation from http://stackoverflow.com/questions/6760685/creating-a-singleton-in-python"""

class Singleton(type):
    """Singleton metaclass; classes of this type will only ever create a single instance"""
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

