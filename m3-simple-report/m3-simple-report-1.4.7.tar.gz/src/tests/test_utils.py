# coding: utf-8
import sys


__author__ = 'prefer'


def skip_python26(f):
    def wrapper(*args, **kwargs):
        if sys.version_info < (2, 7):
            return
        else:
            return f(*args, **kwargs)

    return wrapper
