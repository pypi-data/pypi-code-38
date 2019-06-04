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

import urllib

from linshareapi.core import ResourceBuilder
from linshareapi.core import LinShareException
from linshareapi.user.core import GenericClass
from linshareapi.user.core import Time
from linshareapi.user.core import Cache
from linshareapi.user.core import Invalid

# pylint: disable=missing-docstring
# pylint: disable=too-few-public-methods

class JwtAudit(GenericClass):

    local_base_url = "jwt/audit"

    cache = {
        "familly": "jwt/audit",
        "whole_familly": True
    }

    @Time('audit-list')
    @Cache(discriminant="audit-list", arguments=True)
    def list(self):
        url = "{base}".format(
            base=self.local_base_url
        )
        return self.core.list(url)

    def get_rbu(self):
        rbu = ResourceBuilder("jwt")
        rbu.add_field('action')
        rbu.add_field('creationDate')
        rbu.add_field('authUser')
        rbu.add_field('actor', extended=True)
        rbu.add_field('resource')
        rbu.add_field('uuid', extended=True)
        rbu.add_field('type', extended=True)
        return rbu


class Jwt(GenericClass):

    local_base_url = "jwt"
    # Mandatory: in which familly we want to cache the current resource
    cache = {
        "familly": "jwt",
        "whole_familly": True
    }

    @Time('list')
    @Cache(discriminant="list", arguments=True)
    def list(self):
        """Workaround: data is automatically filtered by domain."""
        # pylint: disable=arguments-differ
        url = "{base}".format(
            base=self.local_base_url
        )
        return self.core.list(url)

    @Time('get')
    @Cache(arguments=True)
    def get(self, uuid):
        """Workaround: missing get entry point"""
        for token in self.list():
            if token.get('uuid') == uuid:
                return token
        raise LinShareException(-1, "Can find uuid:" + uuid)

    def get_rbu(self):
        rbu = ResourceBuilder("jwt")
        rbu.add_field('label')
        rbu.add_field('subject')
        rbu.add_field('uuid')
        rbu.add_field('description')
        rbu.add_field('creationDate')
        rbu.add_field('domain', extended=True)
        rbu.add_field('actor', extended=True)
        rbu.add_field('issuer', extended=True)
        def to_generic_object(value, context):
            # pylint: disable=unused-argument
            return {'uuid': value}
        rbu.add_hook("actor", to_generic_object)
        rbu.add_hook("domain", to_generic_object)
        return rbu
