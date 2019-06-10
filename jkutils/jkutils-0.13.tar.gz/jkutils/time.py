import functools
import logging
import time
from datetime import datetime


def utc_timestamp():
    """返回utc时间戳（秒）"""
    return int(datetime.now().timestamp())


def utc_strftime(fmt):
    """返回格式化的时间"""
    return datetime.now().strftime(fmt)


def print_run_time(func):
    """计算时间函数"""

    @functools.wraps(func)
    def wrapper(*args, **kw):
        local_time = int(time.time() * 1000)
        result = func(*args, **kw)
        logging.info("Function [%s] run time is [%sms]" % (func.__name__, int(time.time() * 1000) - local_time))
        return result

    return wrapper
