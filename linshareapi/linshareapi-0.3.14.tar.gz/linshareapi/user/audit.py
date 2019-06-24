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
from linshareapi.cache import Cache as CCache
from linshareapi.cache import Invalid as IInvalid
from linshareapi.user.core import GenericClass
from linshareapi.user.core import Time as CTime
from linshareapi.user.core import CM



class Time(CTime):
    """TODO"""
    # pylint: disable=too-few-public-methods

    def __init__(self, suffix, **kwargs):
        super(Time, self).__init__('shared_spaces.' + suffix, **kwargs)


class Cache(CCache):
    """TODO"""
    # pylint: disable=too-few-public-methods

    def __init__(self, **kwargs):
        super(Cache, self).__init__(CM, 'shared_spaces', **kwargs)


class Invalid(IInvalid):
    """TODO"""
    # pylint: disable=too-few-public-methods

    def __init__(self, **kwargs):
        super(Invalid, self).__init__(CM, 'shared_spaces', **kwargs)


class Audit(GenericClass):
    """TODO"""

    local_base_url = "audit"

    # cache = {
    #     "familly": "shared_space_audit",
    #     "whole_familly": True,
    # }

    # @Cache(discriminant="audit-list", arguments=True)
    @Time('audit-list')
    def list(self, actions=None, types=None,
             begin_date=None, end_date=None):
        # pylint: disable=arguments-differ
        url = "%(base)s" % {
            'base': self.local_base_url,
        }
        param = {}
        if actions:
            param['action'] = actions
        if types:
            param['type'] = types
        if begin_date:
            param['beginDate'] = begin_date
        if end_date:
            param['endDate'] = end_date
        encode = urllib.urlencode(param, doseq=True)
        if encode:
            url += "?"
            url += encode
        return self.core.list(url)

    @CCache(CM, 'audit-types', cache_duration=3600)
    def types(self):
        """TODO"""
        return self.core.options("enums/audit_log_entry_type")

    @CCache(CM, 'audit-action', cache_duration=3600)
    def actions(self):
        """TODO"""
        return self.core.options("enums/log_action")

    def get_rbu(self):
        rbu = ResourceBuilder("audit")
        rbu.add_field('uuid')
        rbu.add_field('creationDate')
        rbu.add_field('type')
        rbu.add_field('action')
        rbu.add_field('actor')
        rbu.add_field('authUser', extended=True)
        rbu.add_field('workGroup', extended=True)
        rbu.add_field('resourceUuid')
        rbu.add_field('resource')
        return rbu
