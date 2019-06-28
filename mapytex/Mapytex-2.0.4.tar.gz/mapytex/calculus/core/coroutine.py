#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""
Coroutine and sink tools
"""

from functools import wraps

__all__ = ["coroutine", "STOOOP", "RESTAAART"]


def coroutine(func):
    @wraps(func)
    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        next(cr)
        return cr

    return start


class STOOOP(Exception):
    pass


class RESTAAART(Exception):
    pass


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
