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
        super(Time, self).__init__('users.' + suffix, **kwargs)


# -----------------------------------------------------------------------------
class Cache(CCache):
    def __init__(self, **kwargs):
        super(Cache, self).__init__(CM, 'users', **kwargs)


# -----------------------------------------------------------------------------
class Invalid(IInvalid):
    def __init__(self, **kwargs):
        super(Invalid, self).__init__(CM, 'users', **kwargs)


# -----------------------------------------------------------------------------
class Users(GenericClass):

    @Time('search')
    @Cache(arguments=True)
    def search(self, firstname=None, lastname=None, mail=None):
        if not  (firstname or lastname or mail):
            raise ValueError('You should use at least one argument.')
        count = 0
        if firstname:
            count += len(firstname)
        if lastname:
            count += len(lastname)
        if mail:
            count += len(mail)
        if count < 3:
            raise ValueError('You should use at least 3 charaters.')
        criteria = {"firstName": firstname,
                    "lastName": lastname,
                    "mail": mail}
        return self.core.create("users/search", criteria)

    #@InvalidFamilies(CM, 'users')
    def invalid(self):
        return "invalid : ok"

    def autocomplete(self, pattern):
        if not pattern:
            raise ValueError("missing mandatory parameter : pattern")
        return self.core.list("users/autocomplete/%s" % pattern)

    def internals(self, pattern):
        if not pattern:
            raise ValueError("missing mandatory parameter : pattern")
        return self.core.list("users/search/internals/%s" % pattern)

    def guests(self, pattern):
        if not pattern:
            raise ValueError("missing mandatory parameter : pattern")
        return self.core.list("users/search/guests/%s" % pattern)

    def inconsistents(self):
        return self.core.list("users/inconsistent")

    def get_rbu(self):
        rbu = ResourceBuilder("users")
        rbu.add_field('firstName', required=True)
        rbu.add_field('lastName', required=True)
        rbu.add_field('mail', required=True)
        rbu.add_field('uuid')
        rbu.add_field('domain')
        rbu.add_field('guest')
        rbu.add_field('role')
        rbu.add_field('locale')
        rbu.add_field('creationDate')
        rbu.add_field('modificationDate')
        rbu.add_field('canUpload', extended=True)
        rbu.add_field('canCreateGuest', extended=True)
        rbu.add_field('restricted', extended=True)
        rbu.add_field('expirationDate', extended=True)
        rbu.add_field('comment', extended=True)
        rbu.add_field('restrictedContacts', extended=True)
        return rbu
