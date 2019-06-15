# -*- coding: utf-8 -*-
# Copyright (c) 2019 Dzmitry Maliuzhenets; MIT License
"""A module for obtaining information about funcs arguments and their names."""
import inspect


def outer_args(skip_self=True) -> dict:
    """Get the arguments of the func within which this function is called.

    Args:
        skip_self (bool):
            True: skip the argument named `self`
            False: doesn't skip the argument named `self`
    """
    currframe = inspect.currentframe()
    outerframe = inspect.getouterframes(currframe, 2)
    args, _, _, values = inspect.getargvalues(outerframe[1][0])
    if skip_self:  # pylint: disable=R1705
        return {
            key: value
            for key, value in values.items()
            if (key in args) and (key != 'self')
        }
    else:
        return {key: value for key, value in values.items() if key in args}


def outer2_args(skip_self=True):
    """Get outer outer func args.

    Get the arguments of the function, which is an external function for the
    function inside which this function is called.

    Args:
    skip_self (bool):
        True: skip the argument named `self`
        False: doesn't skip the argument named `self`

    Example:
        >>> from telegrambotapiwrapper.frames import outer2_args
        >>> def func(a, b, c):
        ...     def foo(d, e, f):
        ...         args = outer2_args()
        ...         print(args)
        ...     foo(123, 234, 456)
        ... func(567, 678, 789)
        {'a': 567, 'b': 678, 'c': 789}

    """
    currframe = inspect.currentframe()
    outerouterframe = inspect.getouterframes(currframe, 1)
    args, _, _, values = inspect.getargvalues(outerouterframe[2][0])

    if skip_self:  # pylint: disable=R1705
        return {
            key: value
            for key, value in values.items()
            if (key in args) and (key != 'self')
        }
    else:
        return {key: value for key, value in values.items() if key in args}


def outer3_args(skip_self=True):
    """Get outer outer outer func args."""
    currframe = inspect.currentframe()
    outer3frame = inspect.getouterframes(currframe)[3].frame
    args, _, _, values = inspect.getargvalues(outer3frame)

    if skip_self:  # pylint: disable=R1705
        return {
            key: value
            for key, value in values.items()
            if (key in args) and (key != 'self')
        }
    else:
        return {key: value for key, value in values.items() if key in args}


def outer_name():
    """Get the name of the function inside which this function is called."""
    return inspect.stack()[1][3]


def outer2_name():
    """Get the name callel caller name."""
    return inspect.stack()[2][3]


def outer3_name():
    """Get the name caller caller caller name."""
    return inspect.stack()[3][3]
