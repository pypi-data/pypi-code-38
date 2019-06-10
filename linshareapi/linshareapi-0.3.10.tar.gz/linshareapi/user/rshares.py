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
        super(Time, self).__init__('rshares.' + suffix, **kwargs)


# -----------------------------------------------------------------------------
class Cache(CCache):
    def __init__(self, **kwargs):
        super(Cache, self).__init__(CM, 'rshares', **kwargs)


# -----------------------------------------------------------------------------
class Invalid(IInvalid):
    def __init__(self, **kwargs):
        super(Invalid, self).__init__(CM, 'rshares', **kwargs)


# -----------------------------------------------------------------------------
class ReceivedShares(GenericClass):

    @Time('list')
    @Cache()
    def list(self):
        return self.core.list("shares")

    @Time('download')
    def download(self, uuid, directory=None, progress_bar=True):
        url = "shares/%s/download" % uuid
        return self.core.download(uuid, url, directory=directory,
                                  progress_bar=progress_bar)

    @Time('delete')
    @Invalid()
    def delete(self, uuid):
        self.log.warn("Not implemented yed")

    @Time('invalid')
    @Invalid()
    def invalid(self):
        """ List all documents store into LinShare."""
        return "invalid : ok"

    def get_rbu(self):
        rbu = ResourceBuilder("rshares")
        rbu.add_field('name')
        rbu.add_field('size')
        rbu.add_field('uuid')
        rbu.add_field('creationDate')
        rbu.add_field('modificationDate')
        rbu.add_field('type', extended=True)
        rbu.add_field('expirationDate', extended=True)
        rbu.add_field('ciphered', extended=True)
        rbu.add_field('description', extended=True)
        rbu.add_field('message', extended=True)
        rbu.add_field('downloaded', extended=True)
        return rbu


# -----------------------------------------------------------------------------
class ReceivedShares2(ReceivedShares):

    @Time('get')
    def get(self, uuid):
        """ Get one received share."""
        return self.core.get("received_shares/%s" % uuid)

    @Time('list')
    @Cache()
    def list(self):
        return self.core.list("received_shares")

    @Time('download')
    def download(self, uuid, directory=None, progress_bar=True):
        url = "received_shares/%s/download" % uuid
        return self.core.download(uuid, url, directory=directory,
                                  progress_bar=progress_bar)

    @Time('delete')
    @Invalid()
    def delete(self, uuid):
        res = self.get(uuid)
        url = "received_shares/%s" % uuid
        self.core.delete(url)
        return res
