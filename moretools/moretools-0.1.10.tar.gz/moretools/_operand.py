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

"""moretools._operand

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
from six import with_metaclass

__all__ = ['Operand']


class Meta(type):
    """Metaclass for :class:`moretools.Operand`

    - Allows creating Operand subclasses for certain operator functions
      via Operand[<function>]
    """
    def __getitem__(cls, operator):
        class opclass(cls):
            pass

        opclass.operator = staticmethod(operator)
        return opclass


class Operand(with_metaclass(Meta, object)):
    """Base class for creating operand classes.

    - Create subclass with associated operator function
      via Tester[<operator>]
    - Instantiate Operand with right hand operator function args.
    - Complete operation with left hand value
      using <Operand instance>(value)
      which calls <operator>(value, *<right hand args>).
    """
    def __init__(self, *args):
        """Instantiate Operand using `args` as right hand args
           for calling the operator function.
        """
        self.args = args

    def __call__(self, value):
        """Apply class-bound operator function to given left hand `value`
           and stored right hand values.
        """
        return self.operator(value, *self.args)
