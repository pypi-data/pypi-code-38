# MOREtools | MORE Overly Reusable Essentials for Python
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

"""
Tools for creating custom bool classes.

With explicit ``.true`` and ``.false`` lists of valid instantiation values

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""

from six import with_metaclass
from inspect import isclass

import moretools

__all__ = ('StrictBool', 'isboolclass', 'isbool', 'strictbool')


class StrictBoolMeta(type):
    """
    Metaclass for :class:`moretools.StrictBool`.

    And base metaclass used in :func:`moretools.strictbool` class creator

    Makes :class:`moretools.StrictBool`-derived classes behave like built-in
    ``bool`` when used for ``isinstance()`` and ``issubclass()`` checks.
    """

    true = false = None

    def __subclasscheck__(cls, other):
        return other is bool or type.__subclasscheck__(cls, other)

    def __instancecheck__(cls, obj):
        return type(obj) is bool or type.__instancecheck__(cls, obj)

    def __contains__(cls, value):
        """
        Check if `value` is a valid initialization value.

        For the :class:`moretools.StrictBool`-derived `cls`
        """
        return isbool(value) or value in cls.true or value in cls.false


class StrictBool(with_metaclass(StrictBoolMeta, int)):
    """Abstract base class for creating custom bool classes
       with explicit lists of accepted true and false values.

    - Derived classes just have to provide those true and false value lists
      as ``.true`` and ``.false`` class atrributes.
    - Also used as base class by :func:`moretools.strictbool` class creator.
    - By default, instantiation results in a builtin bool value.
    """

    # used by zetup.meta's class __repr__ instead of __module__
    __package__ = moretools.__package__

    def __new__(cls, value):
        if cls is StrictBool:
            raise TypeError("Can't instantiate abstract %s" % repr(cls))
        if isbool(value):
            value = bool(value)
        elif cls.true is not None and value in cls.true:
            value = True
        elif cls.false is not None and value in cls.false:
            value = False
        else:
            raise ValueError(repr(value))
        # return int.__new__(cls, value)
        return value

    def __init__(self, value):
        """Initialize with builtin True or False
           or a `value` contained in either ``.true`` or ``.false`` list
           of this :class:`StrictBool`-derived class
           (or a :class:`StrictBool`-derived instance `value`).
        """
        # all init logic in __new__, which actually returns a builtin bool
        pass

    def __str__(self):
        # only relevant if a derived class overrides __new__
        # to create real StrictBool instances instead of builtin bools
        return str(bool(self))

    def __repr__(self):
        # only relevant if a derived class overrides __new__
        # to create real StrictBool instances instead of builtin bools
        return "<%s: %s>" % (moretools.qualname(type(self)), bool(self))


def strictbool(typename='Bool', true=None, false=None, base=StrictBool):
    """Create a custom bool class which can only be initialized
       with builtin bool values, instances of boolclass()-created classes
       or values contained in the given `true` or `false` sequences.

    - Optionally takes a custom `base` class,
      which must be derived from default ``strictbool.base``
      (:class:`moretools.StrictBool`).
    """
    if not issubclass(base, StrictBool):
        raise TypeError("%s is no subclass of strictbool.base"
                        % repr(base))

    class Meta(type(base)):
        """Metaclass created by moretools.strictbool.
        """
        pass

    # store true and false lists as metaclass attributes
    # to keep it away from instances of created class
    Meta.true = true
    Meta.false = false

    return Meta(typename, (base,), {})


strictbool.base = StrictBool


#: All kinds of boolean types.
bool_types = (bool, StrictBool)


def isboolclass(cls):
    """
    Check if `cls` is built-in ``bool`` or bool-like.

    Which includes all types in :const:`moretools.bool_types`:

    >>> from moretools import StrictBool, isboolclass, strictbool

    >>> isboolclass(bool)
    True

    >>> isboolclass(StrictBool)
    True

    >>> OtherBool = strictbool('OtherBool', true=['yes'], false=['no'])
    >>> isboolclass(OtherBool)
    True

    Checking a non-class object results in a ``TypeError``:

    >>> isboolclass(True)
    Traceback (most recent call last):
    ...
    TypeError: isboolclass() arg must be a class
    """
    if not isclass(cls):
        raise TypeError("isboolclass() arg must be a class")
    return issubclass(cls, (bool, StrictBool))


def isbool(obj):
    """
    Check if `obj` is a built-in ``bool`` or any bool-like instance.

    Which means being an instance of any type in
    :const:`moretools.bool_types`
    """
    return isinstance(obj, (bool, StrictBool))
