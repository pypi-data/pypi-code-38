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
# TO BE REMOVED
# pylint: disable=unused-import
from linshareapi.admin.core import Time
from linshareapi.admin.core import Cache
from linshareapi.admin.core import Invalid

# pylint: disable=missing-docstring
# pylint: disable=too-few-public-methods

class TemplateResource(GenericClass):

    # Mandatory: define the base api for the REST resource
    local_base_url = "my_resource"
    # Mandatory: in which familly we want to cache the current resource
    cache = {"familly": "my_resource"}

    # Mandatory: define the REST resource
    def get_rbu(self):
        rbu = ResourceBuilder("template_resource")
        rbu.add_field('name')
        rbu.add_field('size')
        rbu.add_field('uuid')
        rbu.add_field('creationDate')
        rbu.add_field('modificationDate')
        rbu.add_field('description', extended=True)
        rbu.add_field('sha256sum', extended=True)
        rbu.add_field('metaData', extended=True)
        rbu.add_field(
            'myDomain',
            value={
                'identifier':'LinShareRootDomain',
            },
            arg="domain",
            extended=False,
            required=True)
        return rbu

    # inherited methods:
    #  * def get(self, uuid):
    #  * def delete(self, uuid):
    #  * def list(self):
    #  * def create(self, data):
    #  * def update(self, data):
    #  * def invalid(self):

    # Available annotations:
    #  * @Time('delete') : a wrapper to time a method.
    #  * @Cache() : allow caching the method's result
    #  * @Invalid() : invalid the cache

    @Time('list')
    @Cache(discriminant=True)
    def sample_list(self, domain=None):
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
