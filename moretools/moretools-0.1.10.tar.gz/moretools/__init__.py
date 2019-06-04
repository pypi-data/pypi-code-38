# MOREtools >>> MORE Overly Reusable Essentials for python
#
# Copyright (C) 2011-2019 Stefan Zimmermann <user@zimmermann.co>
#
# MOREtools is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MOREtools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with MOREtools.  If not, see <http://www.gnu.org/licenses/>.

"""MOREtools >>> MORE Overly Reusable Essentials for python."""

__import__('zetup').toplevel(__name__, [
    'SimpleTree',
    'StrictBool',
    'dictitems',
    'dictkeys',
    'dictvalues',
    'func_types',
    'getfunc',
    'isboolclass',
    'isbool',
    'isfunc',
    'qualname',
    'simpledict',
    'strictbool',
    # TODO: fill in rest!
], aliases={
    # six-like aliases for dict... functions
    'iteritems': 'dictitems',
    'iterkeys': 'dictkeys',
    'itervalues': 'dictvalues',
}, deprecated_aliases={
    'Bool': 'StrictBool',
    'boolclass': 'strictbool',
    'booltype': 'strictbool',
    'isbooltype': 'isboolclass',
})


def qualname(cls):
    try:
        return cls.__qualname__
    except AttributeError:
        return cls.__name__


from .boolean import StrictBool, isboolclass, isbool, strictbool
from .func import func_types, getfunc, isfunc

from ._map import *
from .mapping import *
from ._repeat import *
from ._star import *
from ._empty import *
from ._filter import *
from ._query import *
from ._caller import *
from ._get import *
from ._pop import *
from ._set import *
from ._has import *
from ._del import *
from ._collections import *
from ._simpledict import *
from ._dict import *
from ._multi import *
from ._string import *
from ._multidict import *
from ._multisimpledict import *
from ._lazy import *
from ._cached import *
from ._log import *
from ._xmlrpc import *
from ._types import *
from ._operator import *
from ._context import *
from ._simpletree import *

from six.moves import map as _map


class map(object):
    def __init__(self, func):
        self.func = func

    def __call__(self, seq):
        return _map(self.func, seq)

    def __ror__(self, seq):
        return self(seq)


class _(type(is_), type(take)):
    pass


_ = _(is_.op)
