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
# Copyright 2019 Frédéric MARTIN
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


class STime(CTime):
    """TODO"""
    # pylint: disable=too-few-public-methods

    def __init__(self, suffix, **kwargs):
        super(STime, self).__init__('shared_space_members.' + suffix, **kwargs)


class SCache(CCache):
    """TODO"""
    # pylint: disable=too-few-public-methods

    def __init__(self, **kwargs):
        super(SCache, self).__init__(CM, 'shared_space_members', **kwargs)


class SInvalid(IInvalid):
    """TODO"""

    def __init__(self, **kwargs):
        super(SInvalid, self).__init__(CM, 'shared_space_members', **kwargs)


class SharedSpaceMembers(GenericClass):
    """TODO"""

    local_base_url = "shared_spaces"
    local_resource = "members"

    @STime('invalid')
    @SInvalid()
    def invalid(self):
        return "invalid : ok"

    def get_rbu(self):
        rbu = ResourceBuilder("shared_space_member")
        rbu.add_field('uuid')
        rbu.add_field('account', required=True)
        rbu.add_field('role', required=True)
        rbu.add_field('creationDate')
        rbu.add_field('modificationDate')
        rbu.add_field('node', required=True, extended=True)
        rbu.add_field('user', extended=True)
        return rbu

    @STime('list')
    @SCache(arguments=True)
    def list(self, ss_uuid):
        # pylint: disable=arguments-differ
        url = "%(base)s/%(ss_uuid)s/%(resource)s" % {
            'base': self.local_base_url,
            'ss_uuid': ss_uuid,
            'resource': self.local_resource
        }
        return self.core.list(url)

    @STime('get')
    def get(self, ss_uuid, uuid):
        """ Get one contact's list."""
        # pylint: disable=arguments-differ
        url = "%(base)s/%(ss_uuid)s/%(resource)s/%(uuid)s" % {
            'base': self.local_base_url,
            'ss_uuid': ss_uuid,
            'resource': self.local_resource,
            'uuid': uuid
        }
        return self.core.get(url)

    @STime('delete')
    @SInvalid()
    def delete(self, ss_uuid, uuid):
        """ Delete one list."""
        # pylint: disable=arguments-differ
        res = self.get(ss_uuid, uuid)
        url = "%(base)s/%(ss_uuid)s/%(resource)s/%(uuid)s" % {
            'base': self.local_base_url,
            'ss_uuid': ss_uuid,
            'resource': self.local_resource,
            'uuid': uuid
        }
        self.core.delete(url)
        return res

    @STime('update')
    @SInvalid()
    def update(self, data):
        """ Update a list."""
        self.debug(data)
        url = "%(base)s/%(ss_uuid)s/%(resource)s/%(uuid)s" % {
            'base': self.local_base_url,
            'ss_uuid': data.get('mailingListUuid'),
            'resource': self.local_resource,
            'uuid': data.get('uuid')
        }
        return self.core.update(url, data)

    @STime('create')
    @SInvalid()
    def create(self, data):
        self.debug(data)
        self._check(data)
        url = "%(base)s/%(ss_uuid)s/%(resource)s" % {
            'base': self.local_base_url,
            'ss_uuid': data.get('mailingListUuid'),
            'resource': self.local_resource,
        }
        self.core.create(url, data)
        # we return inupt data because res = True (http 204)
        return data


class Time(CTime):
    """TODO"""
    # pylint: disable=too-few-public-methods

    def __init__(self, suffix, **kwargs):
        super(Time, self).__init__('shared_spaces.' + suffix, **kwargs)


class Cache(CCache):
    """TODO"""
    # pylint: disable=too-few-public-methods

    def __init__(self, **kwargs):
        super(Cache, self).__init__(CM, 'shared_spaces', **kwargs)


class Invalid(IInvalid):
    """TODO"""
    # pylint: disable=too-few-public-methods

    def __init__(self, **kwargs):
        super(Invalid, self).__init__(CM, 'shared_spaces', **kwargs)


class SharedSpaces(GenericClass):
    """TODO"""

    local_base_url = "shared_spaces"

    def __init__(self, corecli):
        super(SharedSpaces, self).__init__(corecli)
        self.members = SharedSpaceMembers(corecli)

    @Time('list')
    @Cache()
    def list(self):
        url = self.local_base_url
        return self.core.list(url)

    @Time('invalid')
    @Invalid()
    def invalid(self):
        return "invalid : ok"

    @Time('get')
    def get(self, uuid):
        """ Get one shared_space."""
        url = "%(base)s/%(uuid)s" % {
            'base': self.local_base_url,
            'uuid': uuid
        }
        return self.core.get(url)

    @Time('head')
    def head(self, uuid):
        """ Test if one shared_space exists."""
        url = "%(base)s/%(uuid)s" % {
            'base': self.local_base_url,
            'uuid': uuid
        }
        return self.core.head(url)

    @Time('delete')
    @Invalid()
    def delete(self, uuid):
        """ Delete one shared_space."""
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
        """ Update a shared_space."""
        self.debug(data)
        url = "%(base)s/%(uuid)s" % {
            'base': self.local_base_url,
            'uuid': data.get('uuid')
        }
        return self.core.update(url, data)

    @Time('create')

    def get_rbu(self):
        rbu = ResourceBuilder("shared_space")
        rbu.add_field('uuid')
        rbu.add_field('name')
        rbu.add_field('nodeType')
        rbu.add_field('creationDate')
        rbu.add_field('modificationDate')
        rbu.add_field('parentUuid')
        rbu.add_field('versioningParameters', extended=True)
        rbu.add_field('quotaUuid', extended=True)
        return rbu
