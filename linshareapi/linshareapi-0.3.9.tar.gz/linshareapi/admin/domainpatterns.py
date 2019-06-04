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
        super(Time, self).__init__('domain_patterns.' + suffix, **kwargs)


# -----------------------------------------------------------------------------
class Cache(CCache):
    def __init__(self, **kwargs):
        super(Cache, self).__init__(CM, 'domain_patterns', **kwargs)


# -----------------------------------------------------------------------------
class Invalid(IInvalid):
    def __init__(self, **kwargs):
        super(Invalid, self).__init__(CM, 'domain_patterns', **kwargs)


class DomainPatterns(GenericClass):

    @Time('get')
    def get(self, identifier):
        """ Get one document store into LinShare."""
        documents = (v for v in self.list() if v.get('identifier') == identifier)
        for i in documents:
            self.log.debug(i)
            return i
        return None

    @Time('list')
    @Cache(arguments=True)
    def list(self, model=False):
        if model:
            return self.core.list("domain_patterns/models")
        else:
            return self.core.list("domain_patterns")

    @Time('create')
    @Invalid(whole_familly=True)
    def create(self, data):
        self.debug(data)
        self._check(data)
        return self.core.create("domain_patterns", data)

    @Time('invalid')
    @Invalid()
    def invalid(self):
        return "invalid ok"

    @Time('update')
    @Invalid(whole_familly=True)
    def update(self, data):
        self.debug(data)
        return self.core.update("domain_patterns", data)

    @Time('delete')
    @Invalid(whole_familly=True)
    def delete(self, identifier):
        if identifier:
            identifier = identifier.strip(" ")
        if not identifier:
            raise ValueError("identifier is required")
        res = self.get(identifier)
        self.debug(res)
        data = {"identifier":  identifier}
        self.core.delete("domain_patterns", data)
        return res

    def get_rbu(self):
        rbu = ResourceBuilder("domain_patterns", required=True)
        rbu.add_field('identifier')
        rbu.add_field('description', value="")
        rbu.add_field('userFirstName', 'first_name', extended=True)
        rbu.add_field('userLastName', 'last_name', extended=True)
        rbu.add_field('userMail', 'mail', extended=True)
        rbu.add_field('ldapUid', extended=True)
        rbu.add_field("authCommand", extended=True)
        rbu.add_field("searchUserCommand", extended=True)
        rbu.add_field("autoCompleteCommandOnAllAttributes", extended=True)
        rbu.add_field("autoCompleteCommandOnFirstAndLastName", extended=True)
        rbu.add_field('completionPageSize', extended=True, e_type=int)
        rbu.add_field('completionSizeLimit', extended=True, e_type=int)
        rbu.add_field('searchPageSize', extended=True, e_type=int)
        rbu.add_field('searchSizeLimit', extended=True, e_type=int)
        return rbu

class DomainPatterns2(DomainPatterns):

    @Time('delete')
    @Invalid(whole_familly=True)
    def delete(self, uuid):
        if uuid:
            uuid = uuid.strip(" ")
        if not uuid:
            raise ValueError("uuid is required")
        res = self.get(uuid)
        data = {"uuid":  uuid}
        self.core.delete("domain_patterns", data)
        return res

    @Time('get')
    @Cache()
    def get(self, uuid):
        """ Get one document."""
        return self.core.get("domain_patterns/%s" % uuid)

    def get_rbu(self):
        rbu = ResourceBuilder("domain_patterns", required=True)
        rbu.add_field('uuid')
        rbu.add_field('label', required=True)
        rbu.add_field('description', value="")
        rbu.add_field('userFirstName', 'first_name', extended=True)
        rbu.add_field('userLastName', 'last_name', extended=True)
        rbu.add_field('userMail', 'mail', extended=True)
        rbu.add_field('ldapUid', extended=True)
        rbu.add_field("authCommand", extended=True)
        rbu.add_field("searchUserCommand", extended=True)
        rbu.add_field("autoCompleteCommandOnAllAttributes", extended=True)
        rbu.add_field("autoCompleteCommandOnFirstAndLastName", extended=True)
        rbu.add_field('completionPageSize', extended=True, e_type=int)
        rbu.add_field('completionSizeLimit', extended=True, e_type=int)
        rbu.add_field('searchPageSize', extended=True, e_type=int)
        rbu.add_field('searchSizeLimit', extended=True, e_type=int)
        return rbu
