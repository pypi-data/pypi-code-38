"""Tools for working with or accessing ``function`` objects."""

import types
from doctest import DocTestParser
from inspect import isfunction

from zetup import apifunction

import moretools

__all__ = ('func_types', 'getfunc', 'isfunc')


# used in getfunc()
_wrapper_descriptor_type = type(type.__call__)


#: All types of ``function`` objects.
func_types = (types.BuiltinFunctionType, types.FunctionType, apifunction)


@apifunction(moretools)
def isfunc(obj):
    """
    Check if `obj` is a built-in/user ``function`` or ``zetup.apifunction``.

    In other words, `obj` must be an instance of one of the
    :const:`moretools.func_types`:

    >>> from moretools import isfunc
    >>> isfunc(len)
    True

    >>> def do_something_or_not():
    ...     pass
    >>> isfunc(do_something_or_not)
    True

    >>> import moretools
    >>> from zetup import apifunction

    >>> @apifunction(moretools)
    ... def do_nothing():
    ...     pass

    >>> do_nothing
    <apifunction moretools.do_nothing...>
    >>> isfunc(do_nothing)
    True

    Built-in ``isfunction`` only checks for user-defined functions:

    >>> isfunction(len)
    False
    """
    return isinstance(obj, func_types)


@apifunction(moretools)
def getfunc(obj):
    """
    Get the actual ``function`` object of any ``callable`` `obj`.

    >>> from moretools import getfunc
    >>> class SomeType(object):
    ...     def __call__(self):
    ...         pass

    >>> SomeType().__call__
    <bound method SomeType.__call__ of ...>
    >>> getfunc(SomeType().__call__)
    <function ...__call__ at ...>

    >>> getfunc(SomeType())
    <function ...__call__ at ...>

    If `obj` is a ``function`` itself (as determined by
    :func:`moretools.isfunc`), it will just be returned:

    >>> getfunc(len)
    <built-in function len>

    >>> def do_something_or_not():
    ...     pass
    >>> getfunc(do_something_or_not)
    <function do_something_or_not at ...>

    :raises TypeError:
        if `obj` is not ``callable``
    :raises ValueError:
        if an actual ``function`` object can't be accessed (which usually
        means that it is implemented in C/C++ without being exposed to
        Python)
    """
    if isfunc(obj):
        return obj

    if not callable(obj):
        raise TypeError(
            "{!r} arg is not callable: {!r}".format(getfunc, obj))

    caller = type(obj).__call__
    while caller is not None and not isinstance(
            caller, _wrapper_descriptor_type):
        if isfunc(caller):  # pragma: no py2 cover
            return caller

        else:  # pragma: no py3 cover
            obj = caller
            caller = getattr(type(obj), '__call__', None)
    func = getattr(obj, '__func__', None)
    if isfunc(func):
        return func

    raise ValueError(
        "{!r} can't access function object of callable arg {!r}"
        .format(getfunc, obj))
