from time import time
from pprint import pprint


def profile(func):
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        start = time()
        result = func(*args, **kwargs)
        duration = time() - start
        metrics = {
            'function_name': func_name,
            'total_duration': humanize_time(duration),
        }
        pprint(metrics)
        return result
    return wrapper


def humanize_time(secs):
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return '%02d:%02d:%02d' % (hours, mins, secs)
