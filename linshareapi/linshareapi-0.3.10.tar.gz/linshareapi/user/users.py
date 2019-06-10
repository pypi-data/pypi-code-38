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
from linshareapi.user.core import GenericClass
from linshareapi.user.core import Time as CTime
from linshareapi.user.core import CM

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

    # pylint: disable=R0903
    # Too few public methods (1/2)
    @Time('list')
    @Cache()
    def list(self):
        return self.core.list("users")

    @Time('get')
    def get(self, mail):
        """ Get one document store into LinShare."""
        users = (v for v in self.list() if v.get('mail') == mail)
        for i in users:
            self.log.debug(i)
            return i
        return None

    def get_rbu(self):
        rbu = ResourceBuilder("users")
        rbu.add_field('firstName', required=True)
        rbu.add_field('lastName', required=True)
        rbu.add_field('mail', required=True)
        rbu.add_field('uuid')
        rbu.add_field('domain')
        rbu.add_field('guest')
        rbu.add_field("role")
        rbu.add_field("accountType")
        # Field use less because there are not filled by the server
        #rbu.add_field("canCreateGuest", extended = True)
        #rbu.add_field("canUpload", extended = True)
        #rbu.add_field("restricted", extended = True)
        #rbu.add_field("restrictedContacts", extended = True)
        #rbu.add_field("creationDate", extended = True)
        #rbu.add_field("expirationDate", extended = True)
        #rbu.add_field("modificationDate", extended = True)
        #rbu.add_field("comment", extended = True)
        #rbu.add_field("locale", extended = True)
        #rbu.add_field("externalMailLocale", extended = True)
        return rbu


# -----------------------------------------------------------------------------
class Users2(Users):
    pass
