# coding=utf-8
from __future__ import absolute_import, print_function

import functools
import itertools
import time

from suanpan import utils
from suanpan.log import logger


def formatFuncCall(func, *args, **kwargs):
    paramString = ", ".join(
        itertools.chain(
            (str(a) for a in args), ("{}={}".format(k, v) for k, v in kwargs.items())
        )
    )
    funcString = "{}({})".format(func.__name__, utils.shorten(paramString))
    return funcString


def costCall(func, *args, **kwargs):
    startTime = time.time()
    result = func(*args, **kwargs)
    endTime = time.time()
    costTime = endTime - startTime
    return costTime, result


def cost(func):
    @functools.wraps(func)
    def _dec(*args, **kwargs):
        costTime, result = costCall(func, *args, **kwargs)
        logger.debug("{} - {}s".format(formatFuncCall(func, *args, **kwargs), costTime))
        return result

    return _dec


def print(func):
    @functools.wraps(func)
    def _dec(*args, **kwargs):
        result = func(*args, **kwargs)
        logger.debug("{} - {}".format(formatFuncCall(func, *args, **kwargs), result))
        return result

    return _dec
