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

"""moretools._is

Functional is_() operator function
and functional item processing with logic operators.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from ._common import *

from ._tester import AttrTester, KeyTester
from ._operator import logic_op
from ._operator import *


class _is_(object):
    def __init__(self, is_op):
        self.op = is_op

    def __call__(self, value, *right):
        return self.op(value, *right)

    def __eq__(self, value):
        return eq(value)

    def __ne__(self, value):
        return ne(value)

    def __lt__(self, value):
        return lt(value)

    def __le__(self, value):
        return le(value)

    def __gt__(self, value):
        return gt(value)

    def __ge__(self, value):
        return ge(value)

    def __getattr__(self, attr):
        return _attr_is_(attr)

    def __getitem__(self, key):
        return _key_is_(key)


class _attr_is_(_is_):
    def __init__(self, attr):
        self.attr = attr

    def __eq__(self, value):
        return AttrTester(self.attr, eq(value))

    def __ne__(self, value):
        return AttrTester(self.attr, ne(value))

    def __lt__(self, value):
        return AttrTester(self.attr, lt(value))

    def __le__(self, value):
        return AttrTester(self.attr, le(value))

    def __gt__(self, value):
        return AttrTester(self.attr, gt(value))

    def __ge__(self, value):
        return AttrTester(self.attr, ge(value))


class _key_is_(_is_):
    def __init__(self, key):
        self.key = key

    def __eq__(self, value):
        return KeyTester(self.key, eq(value))

    def __ne__(self, value):
        return KeyTester(self.key, ne(value))

    def __lt__(self, value):
        return KeyTester(self.key, lt(value))

    def __le__(self, value):
        return KeyTester(self.key, le(value))

    def __gt__(self, value):
        return KeyTester(self.key, gt(value))

    def __ge__(self, value):
        return KeyTester(self.key, ge(value))


is_ = _is_(logic_op('is_'))
is_not = _is_(logic_op('is_not'))
