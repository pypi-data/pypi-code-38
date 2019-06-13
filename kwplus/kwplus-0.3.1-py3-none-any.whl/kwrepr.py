from inspect import signature, Parameter, isfunction
from functools import partial

_include_function_defaults = False


def include_function_defaults(value=True):
    global _include_function_defaults
    _include_function_defaults = value


def func_kwrepr(func):
    klass = (func.__name__ if func.__module__ == '__main__'
             else '<lambda:%d>' % id(func) if func.__name__ == '<lambda>'
             else (func.__module__ + ":" + func.__name__))
    if _include_function_defaults:
        kw = {k: kwrepr(v) for k, v in default_kw(func).items()}
        return dict(__class__ = klass, **kw)
    else:
        return dict(__class__ = klass)


def partial_kwrepr(p):
    kwr = dict(__class__ = 'functools:partial',
               func = kwrepr(p.func),
               **{k: kwrepr(v) for k, v in p.keywords.items()})
    if p.args:
        kwr['__args__'] = p.args

    return kwr


def kwrepr(obj):
    return (obj.__kwrepr__()
            if hasattr(obj, "__kwrepr__")
            else partial_kwrepr(obj) if isinstance(obj, partial)
            else func_kwrepr(obj) if isfunction(obj)
            else obj)


def dict_flatten(dct, sep="."):
    if not hasattr(dct, "items"):
        return dct
    flattened_dct = {}
    for key, value in dct.items():
        if hasattr(value, "items"):
            flattened_dct.update(
                {sep.join((key, k)): v
                 for k, v in dict_flatten(value, sep=sep).items()})
        else:
            flattened_dct[key] = value
    return flattened_dct


def flattened_kwrepr(func, sep="."):
    return dict_flatten(kwrepr(func), sep=sep)


def default_kw(func):
    return {k: p.default for k, p in signature(func).parameters.items()
            if p.default is not Parameter.empty}


def need_args(func):
    return [k for k, p in signature(func).parameters.items()
            if p.kind == Parameter.POSITIONAL_OR_KEYWORD]
