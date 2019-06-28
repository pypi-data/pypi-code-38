#/usr/bin/env python
# -*- coding:Utf-8 -*-

from functools import wraps


def number_factory(fun):
    """ Decorator which format returned value """
    @wraps(fun)
    def wrapper(*args, **kwargs):
        ans = fun(*args, **kwargs)
        try:
            if ans.is_integer():
                return int(ans)
            else:
                return round(ans, 2)
        except AttributeError:
            return ans
    return wrapper


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
