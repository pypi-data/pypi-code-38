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
        super(Time, self).__init__('ldaps.' + suffix, **kwargs)


# -----------------------------------------------------------------------------
class Cache(CCache):
    def __init__(self, **kwargs):
        super(Cache, self).__init__(CM, 'ldaps', **kwargs)


# -----------------------------------------------------------------------------
class Invalid(IInvalid):
    def __init__(self, **kwargs):
        super(Invalid, self).__init__(CM, 'ldaps', **kwargs)


# -----------------------------------------------------------------------------
class LdapConnections(GenericClass):

    @Time('get')
    def get(self, identifier):
        """ Get one document store into LinShare."""
        documents = (v for v in self.list() if v.get('identifier') == identifier)
        for i in documents:
            self.log.debug(i)
            return i
        return None

    @Time('list')
    @Cache()
    def list(self):
        return self.core.list("ldap_connections")

    @Time('create')
    @Invalid()
    def create(self, data):
        self.debug(data)
        self._check(data)
        return self.core.create("ldap_connections", data)

    @Time('update')
    @Invalid()
    def update(self, data):
        self.debug(data)
        return self.core.update("ldap_connections", data)

    @Time('delete')
    @Invalid()
    def delete(self, identifier):
        if identifier:
            identifier = identifier.strip(" ")
        if not identifier:
            raise ValueError("identifier is required")
        res = self.get(identifier)
        self.debug(res)
        data = {"identifier":  identifier}
        self.core.delete("ldap_connections", data)
        return res

    def get_rbu(self):
        rbu = ResourceBuilder("ldap_connection")
        rbu.add_field('identifier', required=True)
        rbu.add_field('providerUrl', required=True)
        rbu.add_field('securityPrincipal', "principal")
        rbu.add_field('securityCredentials', "credential")
        return rbu


# -----------------------------------------------------------------------------
class LdapConnections2(LdapConnections):

    @Time('get')
    @Cache()
    def get(self, uuid):
        return self.core.get("ldap_connections/%s" % uuid)

    @Time('delete')
    @Invalid(whole_familly=True)
    def delete(self, uuid):
        if uuid:
            uuid = uuid.strip(" ")
        if not uuid:
            raise ValueError("uuid is required")
        res = self.get(uuid)
        data = {"uuid":  uuid}
        self.core.delete("ldap_connections", data)
        return res

    def get_rbu(self):
        rbu = ResourceBuilder("ldap_connection")
        rbu.add_field('uuid')
        rbu.add_field('label', required=True)
        rbu.add_field('providerUrl', required=True)
        rbu.add_field('securityPrincipal', "principal", extended=True)
        rbu.add_field('securityCredentials', "credential", extended=True)
        return rbu
