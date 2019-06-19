# encoding: utf-8
from django.core.cache import cache



def cacheByTime(seconds=5 * 60):
    """
    根据时间来cache
    """

    def wapper(func):
        def inner(*args):  # 参数必须是位置参数
            key = '{}:{}'.format(func.__name__, args)
            response = cache.get(key)
            if response is not None:
                return response
            response = func(*args)
            cache.set(key, response, seconds)
            return response

        return inner

    return wapper
