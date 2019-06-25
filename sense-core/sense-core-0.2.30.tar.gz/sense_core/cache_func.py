import time
from functools import partial


# 缓存装饰器，缓存方法结果固定时间，默认方法执行结果缓存一天
def cache(fn=None, time_to_live=3600 * 24):  # one DAY default (or whatever)
    if not fn:
        return partial(cache, time_to_live=time_to_live)
    my_cache = {}
    def inner(*args, **kwargs):
        kws = sorted(kwargs.items())
        key = tuple(args) + tuple(kws)
        if key not in my_cache or time.time() > my_cache[key]['expires']:
            my_cache[key] = {"value": fn(*args, **kwargs), "expires": time.time() + time_to_live}
        return my_cache[key]['value']
    return inner