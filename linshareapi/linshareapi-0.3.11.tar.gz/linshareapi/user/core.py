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

from linshareapi.core import GenericClass as GGenericClass
from linshareapi.cache import CacheManager
from linshareapi.cache import Time as CTime
from linshareapi.cache import Cache as CCache
from linshareapi.cache import Invalid as IInvalid


# pylint: disable=missing-docstring
# pylint: disable=too-few-public-methods


CM = CacheManager()

class Time(CTime):
    def __init__(self, suffix, **kwargs):
        super(Time, self).__init__('linshareapi.user.' + suffix, **kwargs)


class Cache(CCache):
    def __init__(self, **kwargs):
        super(Cache, self).__init__(CM, **kwargs)


class Invalid(IInvalid):
    def __init__(self, **kwargs):
        super(Invalid, self).__init__(CM, **kwargs)


class GenericClass(GGenericClass):

    local_base_url = "template_api"
    cache = {}
    # ex: cache = {"familly": "template_api"}

    @Time('get')
    @Cache(arguments=True)
    def get(self, uuid):
        """TODO"""
        url = "{base}/{uuid}".format(
            base=self.local_base_url,
            uuid=uuid
        )
        return self.core.get(url)


    @Time('list')
    @Cache()
    def list(self):
        """TODO"""
        url = "{base}".format(
            base=self.local_base_url
        )
        return self.core.list(url)


    @Time('delete')
    @Invalid()
    def delete(self, uuid):
        """TODO"""
        url = "{base}/{uuid}".format(
            base=self.local_base_url,
            uuid=uuid
        )
        return self.core.delete(url)


    @Time('create')
    @Invalid()
    def create(self, data):
        """TODO"""
        self.debug(data)
        self._check(data)
        return self.core.create(self.local_base_url, data)


    @Time('update')
    @Invalid()
    def update(self, data):
        """TODO"""
        self.debug(data)
        url = "{base}/{uuid}".format(
            base=self.local_base_url,
            uuid=data.get('uuid')
        )
        return self.core.update(url, data)


    # pylint: disable=no-self-use
    @Time('invalid')
    @Invalid()
    def invalid(self):
        """Call this method to invalid the cache."""
        return "invalid : ok"
