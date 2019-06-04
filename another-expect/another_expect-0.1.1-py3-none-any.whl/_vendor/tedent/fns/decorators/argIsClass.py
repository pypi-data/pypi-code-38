from inspect import isclass, signature
from ..._vendor import wrapt


@wrapt.decorator
def argIsClass(fn, _instance, args, kwargs):
    if not isclass(args[0]):
        argName = list(signature(fn).parameters)[0]
        fnName = fn.__name__
        raise ValueError(f"{fnName} requires {argName} to be a class")

    return fn(*args, **kwargs)
