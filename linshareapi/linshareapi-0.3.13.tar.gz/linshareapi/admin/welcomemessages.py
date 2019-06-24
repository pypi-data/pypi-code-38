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
# Copyright 2018 Frédéric MARTIN
#
# Contributors list :
#
#  Frédéric MARTIN frederic.martin.fma@gmail.com
#


from __future__ import unicode_literals
import urllib
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
        super(Time, self).__init__('wlcmesg.' + suffix, **kwargs)


# -----------------------------------------------------------------------------
class Cache(CCache):
    def __init__(self, **kwargs):
        super(Cache, self).__init__(CM, 'wlcmesg', **kwargs)


# -----------------------------------------------------------------------------
class Invalid(IInvalid):
    def __init__(self, **kwargs):
        super(Invalid, self).__init__(CM, 'wlcmesg', **kwargs)


# -----------------------------------------------------------------------------
class WelcomeMessages(GenericClass):

    local_base_url = "welcome_messages"

    def get_rbu(self):
        rbu = ResourceBuilder("welcome_messages")
        rbu.add_field('uuid', required=True)
        rbu.add_field('name', required=True)
        rbu.add_field('modificationDate')
        rbu.add_field('creationDate')
        rbu.add_field('welcomeMessagesEntries', extended=True)
        rbu.add_field('description', extended=True)
        rbu.add_field(
            'myDomain',
            value={
                'identifier':'LinShareRootDomain',
            },
            arg="domain",
            extended=False,
            required=True)
        return rbu

    @Time('invalid')
    @Invalid()
    def invalid(self):
        return "invalid : ok"

    @Time('list')
    @Cache()
    def list(self, domain=None, parent=False):
        url = "{base}".format(
            base=self.local_base_url
        )
        param = {}
        if domain:
            param['domainId'] = domain
        if parent:
            param['parent'] = parent
        encode = urllib.urlencode(param)
        if encode:
            url += "?"
            url += encode
        return self.core.list(url)

    @Time('get')
    def get(self, uuid):
        url = "{base}/{uuid}".format(
            base=self.local_base_url,
            uuid=uuid
        )
        return self.core.get(url)

    @Time('delete')
    @Invalid()
    def delete(self, uuid):
        """ Delete one list."""
        url = "{base}/{uuid}".format(
            base=self.local_base_url,
            uuid=uuid
        )
        return self.core.delete(url)

    @Time('create')
    @Invalid()
    def create(self, data):
        self.debug(data)
        self._check(data)
        return self.core.create(self.local_base_url, data)

    @Time('update')
    @Invalid()
    def update(self, data):
        """ Update a list."""
        self.debug(data)
        url = "{base}/{uuid}".format(
            base=self.local_base_url,
            uuid=data.get('uuid')
        )
        # server does not support uuid in URL for update.
        return self.core.update(self.local_base_url, data)

    @CCache(CM, 'wlcmsg-languages', cache_duration=3600)
    def languages(self):
        return self.core.options("enums/supported_language")
