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

from storops.vnx.resource.fs import VNXFileSystem
from storops.vnx.resource.mover import VNXMover
from storops.vnx.resource import VNXResource, VNXCliResourceList

__author__ = 'Jay Xu'

log = logging.getLogger(__name__)


class VNXFsMountPointList(VNXCliResourceList):
    def __init__(self, mover=None, path=None, cli=None):
        super(VNXFsMountPointList, self).__init__(cli=cli)
        self._mover = mover
        self._path = path

    @classmethod
    def get_resource_class(cls):
        return VNXFsMountPoint

    def _get_raw_resource(self):
        if self._mover:
            mover_id = self._mover.get_mover_id()
            is_vdm = self._mover.is_vdm
        else:
            mover_id = None
            is_vdm = None
        return self._cli.get_fs_mp(
            mover_id=mover_id, is_vdm=is_vdm, path=self._path)


class VNXFsMountPoint(VNXResource):
    def __init__(self, mover=None, path=None, cli=None):
        super(VNXFsMountPoint, self).__init__()
        self._path = path
        self._mover = mover
        self._cli = cli

    def _get_raw_resource(self):
        if self._mover is None:
            raise ValueError('mover not specified.')
        elif self._path is None:
            raise ValueError('path not specified.')
        return self._cli.get_fs_mp(path=self._path,
                                   mover_id=self._mover.get_mover_id(),
                                   is_vdm=self._mover.is_vdm)

    def get_path(self):
        if self._path is not None:
            ret = self._path
        else:
            ret = self.path
        return ret

    @classmethod
    def create(cls, cli, path, fs, mover):
        fs_id = VNXFileSystem.get_id(fs)
        resp = cli.create_fs_mp(path, fs_id, mover.get_mover_id(),
                                mover.is_vdm)
        resp.raise_if_err()
        return VNXFsMountPoint(mover, path, cli)

    def delete(self):
        resp = self._cli.delete_fs_mp(self.get_path(),
                                      self.mover.get_mover_id(),
                                      self.mover.is_vdm)
        resp.raise_if_err()
        return resp

    @property
    def mover(self):
        if self._mover is not None:
            ret = self._mover
        else:
            ret = VNXMover(mover_id=self.mover_id, cli=self._cli)
        return ret

    @property
    def filesystem(self):
        return VNXFileSystem(fs_id=self.fs_id, cli=self._cli)
