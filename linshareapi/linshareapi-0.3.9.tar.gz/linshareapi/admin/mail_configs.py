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
from linshareapi.admin.core import GenericClass
from linshareapi.admin.core import Time
from linshareapi.admin.core import Cache


class MailConfigs(GenericClass):
    """MailConfigs"""

    # Mandatory: define the base api for the REST resource
    local_base_url = "mail_configs"
    cache = {"familly": "mail_configs"}

    def get_rbu(self):
        rbu = ResourceBuilder("mail_configs")
        rbu.add_field('name')
        rbu.add_field('uuid')
        rbu.add_field('domain')
        rbu.add_field('readonly')
        rbu.add_field('visible')
        rbu.add_field('creationDate')
        rbu.add_field('modificationDate')
        rbu.add_field('mailLayout', extended=True)
        return rbu

    @Time('list')
    @Cache(discriminant=True)
    def list(self, domain=None, parent=False):
        # pylint: disable=arguments-differ
        url = "{base}".format(
            base=self.local_base_url
        )
        param = {}
        param['onlyCurrentDomain'] = not parent
        if domain:
            param['domainId'] = domain
        encode = urllib.urlencode(param)
        if encode:
            url += "?"
            url += encode
        return self.core.list(url)
