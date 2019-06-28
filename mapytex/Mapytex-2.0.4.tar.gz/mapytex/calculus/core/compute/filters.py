#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""
Decorator to filter MO before operate
"""

from functools import wraps
from .exceptions import ComputeError


def args_are(left_type, right_type):
    """ Decorator which filter arguments type

    :param left_type: class or tuple of class to pass to isinstance for left arg
    :param right_type: class or tuple of class to pass to isinstance for right arg
    :returns: a decorator which will allow only some type

    """

    def type_filter(func):
        @wraps(func)
        def filtered_func(left, right):
            if not isinstance(left, left_type):
                raise ComputeError(
                    "Wrong type for left argument"
                    f"Require {left_type}, got {left.__class__.__name__}"
                )
            if not isinstance(right, right_type):
                raise ComputeError(
                    "Wrong type for right argument"
                    f"Require {right_type}, got {right.__class__.__name__}"
                )
            return func(left, right)

        return filtered_func

    return type_filter


def special_case(filter):
    """ Decorate operation to filter special cases before call the function

    :param filter: (MO, MO) -> MO or Tree
    :returns: decorator

    """

    def decorator(func):
        @wraps(func)
        def _func(left, right):
            ans = filter(left, right)
            if ans is None:
                return func(left, right)
            return ans

        return _func

    return decorator


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
