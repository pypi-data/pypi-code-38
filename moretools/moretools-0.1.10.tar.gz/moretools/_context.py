# python-moretools
#
# many more basic tools for python 2/3
# extending itertools, functools and operator
#
# Copyright (C) 2011-2014 Stefan Zimmermann <zimmermann.code@gmail.com>
#
# python-moretools is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python-moretools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with python-moretools.  If not, see <http://www.gnu.org/licenses/>.

"""moretools._context

Several string manipulation/converter functions.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from six.moves import zip

__all__ = ['multimethod']

import sys
from inspect import getargspec

from decorator import decorator

from . import qualname


class Method(object):
    def __init__(self, argspec, func, test=None, **args):
        self.argspec = argspec
        self.func = func
        self.test = test
        self.args = args

    def check(self, *args, **kwargs):
        if self.test is not None and not self.test(*args, **kwargs):
            return False
        args = dict(zip(self.argspec.args, args))
        for name, value in self.args.items():
            if name in args and args[name] != value \
              or name in kwargs and kwargs[name] != value:
                return False
        return True


def multimethod(func):
    func_module = func.__module__
    func_name = func.__name__
    func_qualname = qualname(func)

    argspec = getargspec(func)

    def caller(func, self, *args, **kwargs):
        if method.fenter is not None:
            method.fenter(self, *args, **kwargs)
        for dispatch in method.dispatch:
            if dispatch.check(self, *args, **kwargs):
                func = dispatch.func
                break
        else:
            func = method.func
        try:
            return func(self, *args, **kwargs)
        except:
            if method.fexit is not None:
                method.fexit(self, *sys.exc_info())
            else:
                raise

    def enter(func):
        method.fenter = func
        return method

    enter.__module__ = func_module
    enter.__name__ = '%s.enter' % func_name
    enter.__qualname__ = '%s.enter' % func_qualname

    def exit(func):
        method.fexit = func
        return method

    exit.__module__ = func_module
    exit.__name__ = '%s.exit' % func_name
    exit.__qualname__ = '%s.exit' % func_qualname

    def when(test=None, **args):
        def deco(func):
            method.dispatch.append(Method(argspec, func, test, **args))

        return deco

    when.__module__ = func_module
    when.__name__ = '%s.when' % func_name
    when.__qualname__ = '%s.when' % func_qualname

    method = decorator(caller, func)
    method.func = func
    method.dispatch = []
    method.fenter = method.fexit = None
    method.enter = enter
    method.exit = exit
    method.when = when
    return method
