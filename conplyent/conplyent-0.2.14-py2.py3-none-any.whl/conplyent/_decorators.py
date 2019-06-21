from functools import wraps
import time


def timeout(_func=None, name="Timeout"):
    def timeout_decorator(func):
        @wraps(func)
        def timeout_wrapper(*args, **kwargs):
            if("timeout" in kwargs and kwargs["timeout"] is not None):
                start_time = time.perf_counter()
                for none in func(*args, **kwargs):
                    time_taken = time.perf_counter() - start_time
                    if(time_taken > kwargs["timeout"]):
                        raise kwargs["exception"]("{} did not complete in {}s".format(name, time_taken))
                    time.sleep(0)
            else:
                for none in func(*args, **kwargs):
                    time.sleep(0)
        return timeout_wrapper

    return timeout_decorator if(_func is None) else timeout_decorator(_func)
