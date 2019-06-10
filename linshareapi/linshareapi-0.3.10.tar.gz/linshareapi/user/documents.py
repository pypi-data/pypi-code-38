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
        super(Time, self).__init__('documents.' + suffix, **kwargs)


# -----------------------------------------------------------------------------
class Cache(CCache):
    def __init__(self, **kwargs):
        super(Cache, self).__init__(CM, 'documents', **kwargs)


# -----------------------------------------------------------------------------
class Invalid(IInvalid):
    def __init__(self, **kwargs):
        super(Invalid, self).__init__(CM, 'documents', **kwargs)


# -----------------------------------------------------------------------------
class Documents(GenericClass):

    @Time('get')
    def get(self, uuid):
        """ Get one document store into LinShare."""
        #return self.core.get("documents/" + uuid)
        documents = (v for v in self.list() if v.get('uuid') == uuid)
        for i in documents:
            self.log.debug(i)
            return i
        return None

    @Time('list')
    @Cache()
    def list(self):
        """ List all documents store into LinShare."""
        return self.core.list("documents")

    @Time('invalid')
    @Invalid()
    def invalid(self):
        """Invalid local cache"""
        return "invalid : ok"

    @Time('upload')
    @Invalid(whole_familly=True)
    def upload(self, file_path, description=None, async=False):
        """ Upload a file to LinShare using its rest api.
        The uploaded document uuid will be returned"""
        url = "documents?async={a}".format(a=async)
        return self.core.upload(file_path, url, description)

    @Time('upload')
    @Invalid(whole_familly=True)
    def update_file(self, uuid, file_path, async=False):
        """ Upload a file to LinShare using its rest api.
        The uploaded document uuid will be returned"""
        url = "documents/{u}/upload?async={a}".format(u=uuid, a=async)
        return self.core.upload(file_path, url, http_method='PUT')

    @Time('download')
    def download(self, uuid, directory=None, progress_bar=True):
        url = "documents/{u}/download".format(u=uuid)
        return self.core.download(uuid, url, directory=directory,
                                  progress_bar=progress_bar)

    @Time('delete')
    @Invalid(whole_familly=True)
    def delete(self, uuid):
        res = self.get(uuid)
        url = "documents/%s" % uuid
        self.core.delete(url)
        return res

    def get_rbu(self):
        rbu = ResourceBuilder("documents")
        rbu.add_field('name')
        rbu.add_field('size')
        rbu.add_field('uuid')
        rbu.add_field('creationDate')
        rbu.add_field('modificationDate')
        rbu.add_field('type', extended=True)
        rbu.add_field('expirationDate', extended=True)
        rbu.add_field('ciphered', extended=True)
        rbu.add_field('description', extended=True)
        rbu.add_field('sha256sum', extended=True)
        rbu.add_field('metaData', extended=True)
        return rbu


# -----------------------------------------------------------------------------
class Documents2(Documents):

    @Time('get')
    def get(self, uuid):
        """ Get one document."""
        return self.core.get("documents/%s" % uuid)

    @Time('update')
    @Invalid()
    def update(self, data):
        """ Update meta of one document."""
        self.debug(data)
        uuid = data.get('uuid')
        url = "documents/%(uuid)s" % {
            'uuid': uuid,
        }
        return self.core.update(url, data)
