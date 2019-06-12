# coding=utf-8
# Copyright (c) 2015 EMC Corporation.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from __future__ import unicode_literals

import logging

from storops.lib.common import check_int
import storops.vnx.resource.fs
from storops.vnx.resource import VNXResource, VNXCliResourceList

__author__ = 'Cedric Zhuang'

log = logging.getLogger(__name__)


class VNXNasPoolList(VNXCliResourceList):
    @classmethod
    def get_resource_class(cls):
        return VNXNasPool

    def _get_raw_resource(self):
        return self._cli.get_nas_pool()


class VNXNasPool(VNXResource):
    def __init__(self, name=None, pool_id=None, cli=None):
        super(VNXNasPool, self).__init__()
        self._name = name
        self._pool_id = pool_id
        self._cli = cli

    @classmethod
    def get(cls, cli, name=None, pool_id=None):
        if name is not None or pool_id is not None:
            ret = VNXNasPool(name=name, pool_id=pool_id, cli=cli)
        else:
            ret = VNXNasPoolList(cli=cli)
        return ret

    def get_pool_id(self):
        if self._pool_id is not None:
            ret = self._pool_id
        else:
            ret = self.pool_id
        return ret

    @staticmethod
    def get_id(pool):
        if isinstance(pool, VNXNasPool):
            pool = pool.get_pool_id()
        try:
            ret = check_int(pool)
        except ValueError:
            raise ValueError('invalid pool id supplied: {}'
                             .format(pool))
        return ret

    def _get_raw_resource(self):
        resp = self._cli.get_nas_pool()
        resp.filter_object(name=self._name, pool=self._pool_id)
        return resp

    def create_filesystem(self, name, size, mover=1, is_vdm=False):
        fs = storops.vnx.resource.fs
        fs.VNXFileSystem.create(self._cli, name, self, size, mover, is_vdm)
        return fs.VNXFileSystem(name=name, cli=self._cli)
