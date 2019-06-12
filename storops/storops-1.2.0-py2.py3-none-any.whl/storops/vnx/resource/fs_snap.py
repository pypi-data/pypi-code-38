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

import storops.vnx.resource.fs
import storops.vnx.resource.nas_pool
from storops.vnx.resource import VNXCliResourceList, VNXResource

__author__ = 'Jay Xu'

log = logging.getLogger(__name__)


class VNXFsSnapList(VNXCliResourceList):
    @classmethod
    def get_resource_class(cls):
        return VNXFsSnap

    def _get_raw_resource(self):
        return self._cli.get_fs_snap()


class VNXFsSnap(VNXResource):
    def __init__(self, name=None, snap_id=None, cli=None):
        super(VNXFsSnap, self).__init__()
        self._name = name
        self._snap_id = snap_id
        self._cli = cli

    def _get_raw_resource(self):
        if self._name is not None or self._snap_id is not None:
            ret = self._cli.get_fs_snap(self._name, snap_id=self._snap_id)
        else:
            raise ValueError('snap name should be specified.')
        return ret

    @staticmethod
    def get(cli=None, name=None, snap_id=None):
        if name is not None or snap_id is not None:
            ret = VNXFsSnap(name=name, snap_id=snap_id, cli=cli)
        else:
            ret = VNXFsSnapList(cli=cli)
        return ret

    def get_snap_id(self):
        if self._snap_id is not None:
            ret = self._snap_id
        else:
            ret = self.snap_id
        return ret

    @property
    def fs(self):
        clz = storops.vnx.resource.fs.VNXFileSystem
        return clz(fs_id=self.fs_id, cli=self._cli)

    @classmethod
    def create(cls, cli, name, fs, pool, size=None):
        fs_clz = storops.vnx.resource.fs.VNXFileSystem
        pool_clz = storops.vnx.resource.nas_pool.VNXNasPool
        fs_id = fs_clz.get_id(fs)
        pool_id = pool_clz.get_id(pool)
        resp = cli.create_snap(name, fs_id, pool_id, size)
        resp.raise_if_err()
        return VNXFsSnap(name=name, cli=cli)

    def delete(self):
        return self._cli.delete_snap(self.get_snap_id())
