import warnings
from functools import wraps

def deprecated (msg = ""):
    def decorator (f):
        @wraps(f)
        def wrapper (was, *args, **kwargs):
            warnings.simplefilter ('default')
            warnings.warn (
               "{} will be deprecated{}".format (f.__name__, msg and (", " + msg) or ""),
                DeprecationWarning
            )
            return f (was, *args, **kwargs)
        return wrapper
    return decorator
