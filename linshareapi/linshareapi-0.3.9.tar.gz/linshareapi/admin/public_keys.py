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
# Copyright 2018 Frédéric MARTIN
#
# Contributors list :
#
#  Frédéric MARTIN frederic.martin.fma@gmail.com
#


from __future__ import unicode_literals

import urllib

from linshareapi.core import ResourceBuilder
from linshareapi.admin.core import GenericClass
from linshareapi.admin.core import Time
from linshareapi.admin.core import Cache


# pylint: disable=missing-docstring
# pylint: disable=too-few-public-methods

class PublicKeys(GenericClass):

    local_base_url = "public_keys"
    cache = {"familly": "public_keys"}

    @Time('list')
    @Cache(discriminant=True)
    def list(self, domain=None):
        # pylint: disable=arguments-differ
        url = "{base}".format(
            base=self.local_base_url
        )
        param = {}
        if domain:
            param['domain'] = domain
        encode = urllib.urlencode(param)
        if encode:
            url += "?"
            url += encode
        return self.core.list(url)

    def get_rbu(self):
        rbu = ResourceBuilder("public_key")
        rbu.add_field('issuer', required=True)
        rbu.add_field('format', required=True)
        rbu.add_field('creationDate')
        rbu.add_field('uuid')
        rbu.add_field('domainUuid', arg="domain", extended=True)
        rbu.add_field('publicKey', arg="key", extended=True, required=True)
        return rbu
