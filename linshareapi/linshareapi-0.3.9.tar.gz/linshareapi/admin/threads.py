#! /usr/bin/env python
# -*- coding: utf-8 -*-


# This file is part of Linshare api.
#
# LinShare api is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# LinShare api is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LinShare api.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2014 Frédéric MARTIN
#
# Contributors list :
#
#  Frédéric MARTIN frederic.martin.fma@gmail.com
#


from __future__ import unicode_literals

from linshareapi.core import ResourceBuilder
from linshareapi.cache import Cache as CCache
from linshareapi.cache import Invalid as IInvalid
from linshareapi.admin.core import GenericClass
from linshareapi.admin.core import Time as CTime
from linshareapi.admin.core import CM

# pylint: disable=C0111
# Missing docstring
# pylint: disable=R0903
# Too few public methods
# -----------------------------------------------------------------------------
class Time(CTime):
    def __init__(self, suffix, **kwargs):
        super(Time, self).__init__('threads.' + suffix, **kwargs)


# -----------------------------------------------------------------------------
class Cache(CCache):
    def __init__(self, **kwargs):
        super(Cache, self).__init__(CM, 'threads', **kwargs)


# -----------------------------------------------------------------------------
class Invalid(IInvalid):
    def __init__(self, **kwargs):
        super(Invalid, self).__init__(CM, 'threads', **kwargs)


# -----------------------------------------------------------------------------
class Threads(GenericClass):

    @Time('list')
    @Cache()
    def list(self):
        return self.core.list("threads")

    def get_rbu(self):
        rbu = ResourceBuilder("threads")
        rbu.add_field('name', required=True)
        rbu.add_field('domain')
        rbu.add_field('uuid')
        rbu.add_field('creationDate')
        rbu.add_field('modificationDate')
        return rbu
