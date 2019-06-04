# python-moretools
#
# many more basic tools for python 2/3
# extending itertools, functools and operator
#
# Copyright (C) 2011-2016 Stefan Zimmermann <zimmermann.code@gmail.com>
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

"""
Functions for mapping sequence elements to their attrs, items or calls.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""

from ._undefined import undefined
from ._get import getitem

__all__ = ('mapattr', 'mapcall', 'mapitem')


def mapattr(seq, attr, default=undefined):
    """
    Map each element of `seq` to its attribute `attr`.

    Optionally takes a `default` value for elements missing given `attr`.
    Otherwise an AttributeError is raised

    :return: A generator
    """
    if default is undefined:
        for item in seq:
            yield getattr(item, attr)

    else:
        for item in seq:
            yield getattr(item, attr, default)


def mapitem(seq, key, default=undefined):
    """
    Map each element of `seq` to element[`key`].

    Optionally takes a `default` value for elements which raise an IndexError
    or KeyError for the given `key`.

    :return: A generator
    """
    for item in seq:
        yield getitem(item, key, default)


def mapcall(seq, *args, **kwargs):
    """
    Map each element of `seq` to its call result with `args` and `kwargs`.

    :return: A generator
    """
    for item in seq:
        yield item(*args, **kwargs)
