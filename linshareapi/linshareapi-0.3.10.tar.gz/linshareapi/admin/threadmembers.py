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
from linshareapi.admin.core import GenericClass
from linshareapi.admin.core import Time as CTime
from linshareapi.admin.core import CM


class Time(CTime):
    """TODO"""
    # pylint: disable=too-few-public-methods
    def __init__(self, suffix, **kwargs):
        super(Time, self).__init__('tmembers.' + suffix, **kwargs)


class Cache(CCache):
    """TODO"""
    # pylint: disable=too-few-public-methods
    def __init__(self, **kwargs):
        super(Cache, self).__init__(CM, 'tmembers', **kwargs)


class Invalid(IInvalid):
    """TODO"""
    def __init__(self, **kwargs):
        super(Invalid, self).__init__(CM, 'tmembers', **kwargs)


class ThreadsMembers(GenericClass):
    """TODO"""

    @Time('list')
    @Cache()
    def list(self, thread_uuid):
        # pylint: disable=arguments-differ
        url = "thread_members/%s" % thread_uuid
        return self.core.list(url)

    def get_rbu(self):
        rbu = ResourceBuilder("thread_members")
        return rbu


class ThreadsMembers2(ThreadsMembers):
    """TODO"""

    local_base_url = "threads"

    @Time('list')
    @Cache()
    def list(self, thread_uuid):
        url = "%(base)s/%(thread_uuid)s/members" % {
            'base': self.local_base_url,
            'thread_uuid': thread_uuid
        }
        return self.core.list(url)

    @Time('get')
    def get(self, thread_uuid, uuid):
        """ Get one thread member."""
        # pylint: disable=arguments-differ
        members = (v for v in self.list(thread_uuid) if v.get('userUuid') == uuid)
        for i in members:
            self.log.debug(i)
            return i
        return None

    @Time('delete')
    @Invalid()
    def delete(self, thread_uuid, uuid):
        """ Delete one thread member."""
        # pylint: disable=arguments-differ
        res = self.get(thread_uuid, uuid)
        url = "threads/%(t_uuid)s/members/%(uuid)s" % {
            't_uuid': thread_uuid,
            'uuid': uuid
        }
        self.core.delete(url)
        return res

    @Time('update')
    @Invalid()
    def update(self, data):
        """ Update a thread member."""
        self.debug(data)
        # TODO: weird ? missing members ?
        url = "threads/%s" % data.get('uuid')
        return self.core.update(url, data)

    @Time('create')
    @Invalid()
    def create(self, data):
        self.debug(data)
        self._check(data)
        thread_uuid = data.get('threadUuid')
        self.log.debug(thread_uuid)
        url = "threads/%(t_uuid)s/members" % {
            't_uuid': thread_uuid,
        }
        return self.core.create(url, data)

    def get_rbu(self):
        rbu = ResourceBuilder("thread_members")
        rbu.add_field('userUuid')
        rbu.add_field('firstName')
        rbu.add_field('lastName')
        rbu.add_field('userMail', required=True)
        rbu.add_field('role')
        rbu.add_field('admin', extended=True)
        rbu.add_field('readonly', extended=True)
        rbu.add_field('userDomainId', extended=True)
        rbu.add_field('threadUuid', required=True, extended=True)
        return rbu
