#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""TODO"""


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
from linshareapi.user.core import GenericClass
from linshareapi.user.core import Time as CTime
from linshareapi.user.core import CM


class Time(CTime):
    """TODO"""
    # pylint: disable=too-few-public-methods

    def __init__(self, suffix, **kwargs):
        super(Time, self).__init__('threads.' + suffix, **kwargs)


class Cache(CCache):
    """TODO"""
    # pylint: disable=too-few-public-methods

    def __init__(self, **kwargs):
        super(Cache, self).__init__(CM, 'threads', **kwargs)


class Invalid(IInvalid):
    """TODO"""
    # pylint: disable=too-few-public-methods

    def __init__(self, **kwargs):
        super(Invalid, self).__init__(CM, 'threads', **kwargs)


class Threads(GenericClass):
    """TODO"""

    local_base_url = "threads"

    # pylint: disable=R0903
    # Too few public methods (1/2)
    @Time('list')
    @Cache()
    def list(self):
        url = self.local_base_url
        return self.core.list(url)

    @Time('delete')
    @Invalid()
    def delete(self, uuid):
        self.log.warn("Not implemented yed")

    @Time('invalid')
    @Invalid()
    def invalid(self):
        return "invalid : ok"

    def get_rbu(self):
        rbu = ResourceBuilder("threads")
        rbu.add_field('name', required=True)
        rbu.add_field('uuid')
        rbu.add_field('creationDate')
        rbu.add_field('modificationDate')
        rbu.add_field('domain', extended=True)
        return rbu


class Threads2(Threads):
    """TODO"""

    @Time('get')
    def get(self, uuid):
        """ Get one thread."""
        url = "%(base)s/%(uuid)s" % {
            'base': self.local_base_url,
            'uuid': uuid
        }
        return self.core.get(url)

    @Time('head')
    def head(self, uuid):
        """ Get one thread."""
        url = "%(base)s/%(uuid)s" % {
            'base': self.local_base_url,
            'uuid': uuid
        }
        return self.core.head(url)

    @Time('delete')
    @Invalid()
    def delete(self, uuid):
        """ Delete one thread."""
        res = self.get(uuid)
        url = "%(base)s/%(uuid)s" % {
            'base': self.local_base_url,
            'uuid': uuid
        }
        self.core.delete(url)
        return res

    @Time('update')
    @Invalid()
    def update(self, data):
        """ Update a thread."""
        self.debug(data)
        url = "%(base)s/%(uuid)s" % {
            'base': self.local_base_url,
            'uuid': data.get('uuid')
        }
        return self.core.update(url, data)

    @Time('create')
    @Invalid()
    def create(self, data):
        self.debug(data)
        self._check(data)
        url = self.local_base_url
        return self.core.create(url, data)


class Workgroup(Threads2):
    """TODO"""

    local_base_url = "work_groups"
