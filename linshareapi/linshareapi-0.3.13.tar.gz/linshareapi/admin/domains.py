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


# -----------------------------------------------------------------------------
# global config
# pylint: disable=missing-docstring


# -----------------------------------------------------------------------------
class Time(CTime):
    # pylint: disable=too-few-public-methods
    def __init__(self, suffix, **kwargs):
        super(Time, self).__init__('domains.' + suffix, **kwargs)


# -----------------------------------------------------------------------------
class Cache(CCache):
    # pylint: disable=too-few-public-methods
    def __init__(self, **kwargs):
        super(Cache, self).__init__(CM, 'domains', **kwargs)


# -----------------------------------------------------------------------------
class Invalid(IInvalid):
    # pylint: disable=too-few-public-methods
    def __init__(self, **kwargs):
        super(Invalid, self).__init__(CM, 'domains', **kwargs)


# -----------------------------------------------------------------------------
class Domains(GenericClass):

    @Time('get')
    def get(self, identifier):
        """ Get one domain."""
        # return self.core.get("domains/" + identifier)
        domains = (v for v in self.list() if v.get('identifier') == identifier)
        for i in domains:
            self.log.debug(i)
            return i
        return None

    @Time('list')
    @Cache()
    def list(self):
        return self.core.list("domains")

    @Time('create')
    @Invalid()
    def create(self, data):
        self.debug(data)
        if data.get('label') is None:
            data['label'] = data.get('identifier')
        self._check(data)
        if data.get('type') in ["GUESTDOMAIN", "SUBDOMAIN"]:
            if data.get('parent') is None:
                raise ValueError(
                    "parent identifier is required for GuestDomain / SubDomain"
                )
        return self.core.create("domains", data)

    @Time('update')
    @Invalid()
    def update(self, data):
        self.debug(data)
        return self.core.update("domains", data)

    @Time('delete')
    @Invalid()
    def delete(self, identifier):
        if identifier:
            identifier = identifier.strip(" ")
        if not identifier:
            raise ValueError("identifier is required")
        obj = self.get(identifier)
        data = {"identifier":  identifier}
        self.core.delete("domains", data)
        return obj

    @CCache(CM, 'domain-lang', cache_duration=3600)
    def options_language(self):
        return self.core.options("enums/language")

    @CCache(CM, 'domain-lang-mail', cache_duration=3600)
    def options_mail_language(self):
        return self.core.options("enums/language")

    def options_role(self):
        # pylint: disable=R0201
        return ['ADMIN', 'SIMPLE']

    def options_type(self):
        # pylint: disable=R0201
        return ['GUESTDOMAIN', 'SUBDOMAIN', 'TOPDOMAIN']

    def get_rbu(self):
        rbu = ResourceBuilder("domains")
        rbu.add_field('identifier', required=True)
        rbu.add_field('label', required=True)
        rbu.add_field('policy', value={"identifier": "DefaultDomainPolicy"},
                      hidden=True)
        rbu.add_field('type', "domain_type", value="TOPDOMAIN")
        rbu.add_field('parent', "parent_id")
        rbu.add_field('language', value="ENGLISH")
        rbu.add_field('userRole', "role", value="SIMPLE")
        rbu.add_field('mailConfigUuid',
                      value="946b190d-4c95-485f-bfe6-d288a2de1edd",
                      extended=True)
        rbu.add_field('mimePolicyUuid',
                      value="3d6d8800-e0f7-11e3-8ec0-080027c0eef0",
                      extended=True)
        rbu.add_field('description', value="")
        rbu.add_field('authShowOrder', value="1", extended=True)
        rbu.add_field('providers', value=[], extended=True)
        rbu.add_field('currentWelcomeMessages',
                      value={'uuid': "4bc57114-c8c9-11e4-a859-37b5db95d856"},
                      extended=True)
        rbu.add_field('externalMailLocale', value="ENGLISH")
        return rbu


# -----------------------------------------------------------------------------
class Domains2(Domains):

#    @Time('get')
#    @Cache()
#    def get(self, identifier):
#        """ Get one domain."""
#        url = "domains/{i}".format({"i": identifier})
#        return self.core.get(url)

    def get_rbu(self):
        rbu = ResourceBuilder("domains")
        rbu.add_field('identifier', required=True)
        rbu.add_field('label', required=True)
        rbu.add_field('policy', value={"identifier": "DefaultDomainPolicy"},
                      hidden=True)
        rbu.add_field('type', "domain_type", value="TOPDOMAIN")
        rbu.add_field('parent', "parent_id", extended=True)
        rbu.add_field('language', value="ENGLISH", extended=True)
        rbu.add_field('externalMailLocale', value="ENGLISH", extended=True)
        rbu.add_field('userRole', "role", value="SIMPLE")
        rbu.add_field('mailConfigUuid',
                      value="946b190d-4c95-485f-bfe6-d288a2de1edd",
                      extended=True)
        rbu.add_field('mimePolicyUuid',
                      value="3d6d8800-e0f7-11e3-8ec0-080027c0eef0",
                      extended=True)
        rbu.add_field('description', value="", extended=True)
        rbu.add_field('authShowOrder', value="1", extended=True)
        rbu.add_field('providers', value=[], extended=True)
        rbu.add_field('currentWelcomeMessage',
                      value={'uuid': "4bc57114-c8c9-11e4-a859-37b5db95d856"},
                      extended=True)
        return rbu
