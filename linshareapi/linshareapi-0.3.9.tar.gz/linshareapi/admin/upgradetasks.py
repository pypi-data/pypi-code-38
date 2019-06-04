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
# Copyright 2018 Frédéric MARTIN
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
        super(Time, self).__init__('up_tasks.' + suffix, **kwargs)


# -----------------------------------------------------------------------------
class Cache(CCache):
    def __init__(self, **kwargs):
        super(Cache, self).__init__(CM, 'up_tasks', **kwargs)


# -----------------------------------------------------------------------------
class Invalid(IInvalid):
    def __init__(self, **kwargs):
        super(Invalid, self).__init__(CM, 'up_tasks', **kwargs)


# -----------------------------------------------------------------------------
class ConsoleUpgradeTasks(GenericClass):

    local_base_url = "upgrade_tasks"

    def get_rbu(self):
        rbu = ResourceBuilder("console")
        rbu.add_field('creationDate')
        rbu.add_field('criticity')
        rbu.add_field('message')
        rbu.add_field('asyncTask', extended=True)
        rbu.add_field('upgradeTask', extended=True)
        # rbu.add_field('waitingDuration', hidden=True)
        return rbu

    @Time('console.list')
    def list(self, identifier, uuid):
        url = "{base}/{identifier}/async_tasks/{uuid}/console".format(
            base=self.local_base_url,
            identifier=identifier,
            uuid=uuid
        )
        return self.core.get(url)


class AsyncUpgradeTasks(GenericClass):

    local_base_url = "upgrade_tasks"

    def __init__(self, corecli):
        super(AsyncUpgradeTasks, self).__init__(corecli)
        self.console = ConsoleUpgradeTasks(corecli)

    def get_rbu(self):
        rbu = ResourceBuilder("async_tasks")
        rbu.add_field('uuid')
        rbu.add_field('fileName')
        rbu.add_field('status')
        rbu.add_field('creationDate')
        rbu.add_field('processingDuration', extended=True)
        rbu.add_field('resourceUuid', extended=True)
        rbu.add_field('modificationDate', extended=True)
        rbu.add_field('errorName', extended=True)
        rbu.add_field('errorCode', extended=True)
        rbu.add_field('errorMsg', extended=True)
        rbu.add_field('frequency', hidden=True)
        rbu.add_field('transfertDuration', hidden=True)
        rbu.add_field('waitingDuration', hidden=True)
        return rbu

    @Time('async.list')
    def list(self, identifier):
        url = "{base}/{identifier}/async_tasks".format(
            base=self.local_base_url,
            identifier=identifier
        )
        return self.core.get(url)

    @Time('async.get')
    def get(self, identifier, uuid):
        url = "{base}/{identifier}/async_tasks/{uuid}".format(
            base=self.local_base_url,
            identifier=identifier,
            uuid=uuid
        )
        return self.core.get(url)


class UpgradeTasks(GenericClass):

    local_base_url = "upgrade_tasks"

    def __init__(self, corecli):
        super(UpgradeTasks, self).__init__(corecli)
        self.async_tasks = AsyncUpgradeTasks(corecli)

    def get_rbu(self):
        rbu = ResourceBuilder("upgrade_tasks")
        rbu.add_field('identifier', required=True)
        rbu.add_field('taskOrder')
        rbu.add_field('status')
        rbu.add_field('priority')
        rbu.add_field('creationDate')
        rbu.add_field('modificationDate')
        rbu.add_field('parentIdentifier', extended=True)
        rbu.add_field('taskGroup', extended=True)
        rbu.add_field('asyncTaskUuid', extended=True)
        return rbu

    @Time('invalid')
    @Invalid()
    def invalid(self):
        return "invalid : ok"

    @Time('list')
    @Cache()
    def list(self):
        return self.core.list(self.local_base_url)

    @Time('get')
    def list_async(self, identifier):
        url = "{base}/{identifier}/async_tasks".format(
            base=self.local_base_url,
            identifier=identifier
        )
        return self.core.get(url)

    @Time('get')
    def get(self, identifier):
        url = "{base}/{identifier}".format(
            base=self.local_base_url,
            identifier=identifier
        )
        return self.core.get(url)

    @Time('trigger')
    @Invalid()
    def trigger(self, identifier, force=True):
        """Trigger an upgrade task."""
        self.debug(identifier)
        url = "{base}/{identifier}".format(
            base=self.local_base_url,
            identifier=identifier
        )
        param = {}
        if force:
            param['force'] = force
        encode = urllib.urlencode(param)
        if encode:
            url += "?"
            url += encode
        return self.core.update(url, {})
