from inspect import signature
from ..._vendor import wrapt


@wrapt.decorator
def argIsCallable(fn, _instance, args, kwargs):
    if not callable(args[0]):
        argName = list(signature(fn).parameters)[0]
        fnName = fn.__name__
        raise ValueError(f"{fnName} requires {argName} to be callable")

    return fn(*args, **kwargs)
