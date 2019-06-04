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
# Copyright 2017 Frédéric MARTIN
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
        super(Time, self).__init__('contactslistcontact.' + suffix, **kwargs)


class Cache(CCache):
    """TODO"""
    # pylint: disable=too-few-public-methods

    def __init__(self, **kwargs):
        super(Cache, self).__init__(CM, 'contactslistcontact', **kwargs)


class Invalid(IInvalid):
    """TODO"""

    def __init__(self, **kwargs):
        super(Invalid, self).__init__(CM, 'contactslistcontact', **kwargs)


class ContactsListContact(GenericClass):
    """TODO"""


    local_base_url = "lists"

    @Time('invalid')
    @Invalid()
    def invalid(self):
        return "invalid : ok"

    def get_rbu(self):
        rbu = ResourceBuilder("contactslistcontact")
        rbu.add_field('uuid')
        rbu.add_field('mail', required=True)
        rbu.add_field('firstName')
        rbu.add_field('lastName')
        rbu.add_field('mailingListUuid', extended=True)
        return rbu

    @Time('list')
    @Cache()
    def list(self, list_uuid):
        # pylint: disable=arguments-differ
        url = "%(base)s/%(list_uuid)s/contacts" % {
            'base': self.local_base_url,
            'list_uuid': list_uuid
        }
        return self.core.list(url)

    @Time('get')
    def get(self, list_uuid, uuid):
        """ Get one contact's list."""
        # pylint: disable=arguments-differ
        url = "%(base)s/%(list_uuid)s/contacts/%(uuid)s" % {
            'base': self.local_base_url,
            'list_uuid': list_uuid,
            'uuid': uuid
        }
        return self.core.get(url)

    @Time('delete')
    @Invalid()
    def delete(self, list_uuid, uuid):
        """ Delete one list."""
        # pylint: disable=arguments-differ
        res = self.get(list_uuid, uuid)
        url = "%(base)s/%(list_uuid)s/contacts/%(uuid)s" % {
            'base': self.local_base_url,
            'list_uuid': list_uuid,
            'uuid': uuid
        }
        self.core.delete(url)
        return res

    @Time('update')
    @Invalid()
    def update(self, data):
        """ Update a list."""
        self.debug(data)
        url = "%(base)s/%(list_uuid)s/contacts/%(uuid)s" % {
            'base': self.local_base_url,
            'list_uuid': data.get('mailingListUuid'),
            'uuid': data.get('uuid')
        }
        return self.core.update(url, data)

    @Time('create')
    @Invalid()
    def create(self, data):
        self.debug(data)
        self._check(data)
        url = "%(base)s/%(list_uuid)s/contacts" % {
            'base': self.local_base_url,
            'list_uuid': data.get('mailingListUuid')
        }
        self.core.create(url, data)
        # we return inupt data because res = True (http 204)
        return data


class ContactsListContact2(ContactsListContact):
    """TODO"""

    local_base_url = "contact_lists"

    @Time('get')
    def get(self, list_uuid, uuid):
        """ Get one contact's list."""
        # workaround
        res = self.list(list_uuid)
        for elt in res:
            if elt.get('uuid') == uuid:
                return elt
        return None

    @Time('delete')
    @Invalid()
    def delete(self, list_uuid, uuid):
        """ Delete one list."""
        res = self.get(list_uuid, uuid)
        url = "%(base)s/%(list_uuid)s/contacts/%(uuid)s" % {
            'base': self.local_base_url,
            'list_uuid': list_uuid,
            'uuid': uuid
        }
        self.core.delete(url)
        return res
