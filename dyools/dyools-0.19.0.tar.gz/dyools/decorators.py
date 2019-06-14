from __future__ import (absolute_import, division, print_function, unicode_literals)

import time
from functools import wraps
from pprint import pformat

from .klass_convert import Convert
from .klass_print import Print
from .klass_str import Str


def log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        infos = ['Call -> function: %r' % func]
        for i, arg in enumerate(args):
            infos.append('  arg   %20s-%02d: %20s => %s' % (id(arg), i, type(arg), pformat(arg)))
        for key, value in kwargs.items():
            infos.append('  kwarg %20s-%10s: %20s => %s ' % (id(arg), key, type(value), pformat(value)))
        start = time.time()
        res = func(*args, **kwargs)
        elapsed_time = Convert.time(time.time() - start, 's', 's', 2)
        infos.append('  result %22s: %20s => %s ' % (id(arg), type(res), pformat(res)))
        infos.append('  elapsed time: %s' % Str(elapsed_time, suffix='second(s)'))
        Print.info('\n'.join(infos))
        return res

    return wrapper


def raise_exception(exception=Exception, exception_msg='Error'):
    def real_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _raise = kwargs.pop('exception', False)
            _args = list(args)[1::]
            for k, v in kwargs.items():
                _args.append(v)
            res = func(*args, **kwargs)
            if _raise and not res:
                raise exception(exception_msg % tuple(_args))
            return res

        return wrapper

    return real_decorator
