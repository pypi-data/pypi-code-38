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

import urllib2
import datetime

from linshareapi.core import ResourceBuilder
from linshareapi.cache import Cache as CCache
from linshareapi.cache import Invalid as IInvalid
from linshareapi.user.core import GenericClass
from linshareapi.user.core import Time as CTime
from linshareapi.user.core import CM

# pylint: disable=C0111
# Missing docstring
# pylint: disable=R0903
# Too few public methods
# -----------------------------------------------------------------------------
class Time(CTime):
    def __init__(self, suffix, **kwargs):
        super(Time, self).__init__('shares.' + suffix, **kwargs)


# -----------------------------------------------------------------------------
class Cache(CCache):
    def __init__(self, **kwargs):
        super(Cache, self).__init__(CM, 'shares', **kwargs)


# -----------------------------------------------------------------------------
class Invalid(IInvalid):
    def __init__(self, **kwargs):
        super(Invalid, self).__init__(CM, 'shares', **kwargs)


# -----------------------------------------------------------------------------
class Shares(GenericClass):

    # pylint: disable=R0903
    # Too few public methods (1/2)
    def share(self, uuid, mail):
        url = self.core.get_full_url(
            "shares/sharedocument/%s/%s" % (mail, uuid))
        self.log.debug("share url : " + url)
        # Building request
        request = urllib2.Request(url)
        # request start
        starttime = datetime.datetime.now()
        try:
            # doRequest
            resultq = urllib2.urlopen(request)
        except urllib2.HTTPError as ex:
            print ex
            print ex.code
            print url
            raise ex
        # request end
        endtime = datetime.datetime.now()
        code = resultq.getcode()
        msg = resultq.msg
        self.core.last_req_time = str(endtime - starttime)
        self.log.debug("share url : %(url)s : request time : %(time)s",
                       {"url": url,
                        "time": self.core.last_req_time})
        self.log.debug("the result is : " + str(code) + " : " + msg)
        return (code, msg, self.core.last_req_time)


# -----------------------------------------------------------------------------
class Shares2(Shares):

    def get_rbu(self):
        rbu = ResourceBuilder("shares")
        rbu.add_field('secured', e_type=bool)
        rbu.add_field('expirationDate')
        rbu.add_field('subject')
        rbu.add_field('message')
        # [document uuids,]
        rbu.add_field('documents', required=True)
        # [GenericUserDto,]
        rbu.add_field('recipients',required=True)
        return rbu

    def get_rbu_user(self):
        rbu = ResourceBuilder("GenericUserDto")
        rbu.add_field('mail')
        rbu.add_field('uuid')
        rbu.add_field('domain')
        rbu.add_field('firstName')
        rbu.add_field('lastName')
        return rbu

    @Time('create')
    @Invalid()
    def create(self, data):
        self.debug(data)
        self._check(data)
        return self.core.create("shares", data)
