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
        super(Time, self).__init__('functionalities.' + suffix, **kwargs)


# -----------------------------------------------------------------------------
class Cache(CCache):
    def __init__(self, **kwargs):
        super(Cache, self).__init__(CM, 'functionalities', **kwargs)


# -----------------------------------------------------------------------------
class Invalid(IInvalid):
    def __init__(self, **kwargs):
        super(Invalid, self).__init__(CM, 'functionalities', **kwargs)


# -----------------------------------------------------------------------------
class Functionalities(GenericClass):

    @Time('list')
    @Cache(arguments=True)
    def list(self, domain_id=None, only_parents=False):
        if domain_id is None:
            domain_id = "LinShareRootDomain"
        url = "functionalities?domainId={d}&subs={s!s}"
        url = url.format(d=domain_id, s=only_parents)
        json_obj = self.core.list(url)
        return [row for row in json_obj if row.get('displayable') == True]

    @Cache(discriminant="get", arguments=True)
    def get(self, func_id, domain_id=None):
        if domain_id is None:
            domain_id = "LinShareRootDomain"
        json_obj = self.core.get("functionalities/"+ func_id +"?domainId=" +
                                 domain_id)
        return json_obj

    @Invalid(whole_familly=True)
    def invalid(self):
        return "invalid : ok"

    @Time('update')
    @Invalid()
    def update(self, data):
        self.debug(data)
        return self.core.update("functionalities", data)

    @Time('reset')
    @Invalid()
    def reset(self, data):
        self.debug(data)
        return self.core.delete("functionalities", data)

    def options_policies(self):
        return self.core.options("enums/policies")

    def get_rbu(self):
        rbu = ResourceBuilder("functionality")
        rbu.add_field('identifier', required=True)
        rbu.add_field('type')
        rbu.add_field('activationPolicy', required=False)
        rbu.add_field('configurationPolicy', extended=True, required=False)
        rbu.add_field('delegationPolicy', extended=True, required=False)
        rbu.add_field('parameters')
        rbu.add_field('parentIdentifier', extended=True)
        #rbu.add_field('functionalities', extended=True)
        rbu.add_field('domain', extended=True, required=True)
        rbu.add_field('parentAllowParametersUpdate', extended=True)
        return rbu
