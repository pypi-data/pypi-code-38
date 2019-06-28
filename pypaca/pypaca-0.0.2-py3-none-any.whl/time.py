from datetime import datetime


def timer(func):
    """A decorator that times and prints execution time."""
    def timer_wrapper(*args, **kwargs):
        start_time = datetime.now()
        resp = func(*args, **kwargs)
        end_time = datetime.now()
        duration = end_time - start_time
        print("{:<40} runtime: {}.{} secs".format(
            func.__name__, duration.seconds, duration.microseconds))
        return resp
    return timer_wrapper


def busy_try(delay_secs: int, ExceptionType=Exception):
    """
    A decorator that repeatedly attempts the function until the timeout specified 
    has been reached. This is different from timeout-related functions, where
    the decorated function is called only *once*.
    
    Because the decorated function is called repeatedly, the delay period should 
    not be long. Use `timeout` if you hope to avoid occupying system resources.

    Parameters
    ----------
    delay_secs : 
        time delayed, in seconds.
    ExceptionType : optional
        exception caught when the function attempted raises an error. Default
        to `Exception`.

    Returns
    -------
    The return value of the decorated function, if any function call is 
    successful; `None`, otherwise.

    Raises
    ------
    TimeoutError : 
        when the function has tried `delayed_secs` seconds and no function call
        succeeds.
    """
    def _busy_try(func):
        @functools.wraps(func)
        def busy_try_wrapper(self, *args, **kwargs):
            start = datetime.now()
            while True:
                try:
                    return func(self, *args, **kwargs)
                except ExceptionType:
                    continue
                finally:
                    now = datetime.now()
                    if (now - start).seconds > delay_secs:
                        raise TimeoutError
                        break
            return None
        return busy_try_wrapper
    return _busy_try
