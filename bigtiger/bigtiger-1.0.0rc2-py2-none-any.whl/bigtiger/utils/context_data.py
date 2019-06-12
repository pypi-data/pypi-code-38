# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

import functools


def to_entity(fn):
    """通过fields在context_data中抽取实体"""

    @functools.wraps(fn)
    def _context_data2entity(*args, **kwargs):
        cd, fields = fn(*args, **kwargs)
        d = {}
        for field in fields:
            d[field] = cd.get(field, None)
        return d
    return _context_data2entity
