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

from linshareapi.core import ResourceBuilder
from linshareapi.core import LinShareException
from linshareapi.admin.core import GenericClass
from linshareapi.admin.core import Time

# pylint: disable=missing-docstring
# pylint: disable=too-few-public-methods


class Authentication(GenericClass):

    cache = {
        "familly": "authentication",
    }

    local_base_url = "authentication"

    @Time('list')
    def list(self):
        url = "{base}/authorized".format(
            base=self.local_base_url
        )
        return [self.core.get(url)]

    @Time('update')
    def update(self, data):
        """ Update a list."""
        # if self.debug >= 2:
        #     self.debug(data)
        url = "{base}/change_password".format(
            base=self.local_base_url
        )
        self._check(data)
        res = self.core.create(url, data)
        self.log.debug("result: %s", res)
        return res

    def get_rbu(self):
        rbu = ResourceBuilder("users")
        rbu.add_field('uuid')
        rbu.add_field('mail')
        rbu.add_field('firstName')
        rbu.add_field('lastName')
        rbu.add_field('domain')
        rbu.add_field('role')
        rbu.add_field('accountType', extended=True)
        rbu.add_field('locale', extended=True)
        rbu.add_field('externalMailLocale')
        rbu.add_field('creationDate')
        rbu.add_field('modificationDate')
        rbu.add_field('canUpload', extended=True)
        rbu.add_field('canCreateGuest', extended=True)
        return rbu

    def get_rbu_update(self):
        rbu = ResourceBuilder("password")
        rbu.add_field('oldPwd', required=True)
        rbu.add_field('newPwd', required=True)
        return rbu
