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
import re

import six

from storops.connection.exceptions import SSHExecutionError
from storops.lib.common import check_int
import storops.vnx.resource.mover
import storops.vnx.resource.nas_pool
from storops.vnx.resource import VNXResource, VNXCliResourceList
from storops.vnx.resource.fs_snap import VNXFsSnap

__author__ = 'Jay Xu'

LOG = logging.getLogger(__name__)


class VNXFileSystemList(VNXCliResourceList):
    @classmethod
    def get_resource_class(cls):
        return VNXFileSystem

    def _get_raw_resource(self):
        return self._cli.get_filesystem()


class VNXFileSystem(VNXResource):
    def __init__(self, name=None, fs_id=None, cli=None):
        super(VNXFileSystem, self).__init__()
        self._name = name
        self._fs_id = fs_id
        self._cli = cli

    @classmethod
    def get(cls, cli, name=None, fs_id=None):

        if name is not None or fs_id is not None:
            ret = VNXFileSystem(name=name, fs_id=fs_id, cli=cli)
        else:
            ret = VNXFileSystemList(cli=cli)
        return ret

    def get_name(self):
        return self._get_name()

    def get_fs_id(self):
        if self._fs_id is not None:
            ret = self._fs_id
        else:
            ret = self.fs_id
        return ret

    @staticmethod
    def get_id(fs):
        if isinstance(fs, VNXFileSystem):
            fs = fs.get_fs_id()
        try:
            ret = check_int(fs)
        except ValueError:
            raise ValueError('invalid fs id supplied: {}'
                             .format(fs))
        return ret

    def _get_raw_resource(self):
        if self._name is not None:
            ret = self._cli.get_filesystem(self._name)
        elif self._fs_id is not None:
            ret = self._cli.get_filesystem(fs_id=self._fs_id)
        else:
            raise ValueError('fs id or name should be specified.')
        return ret

    @staticmethod
    def create(cli, name, pool, size_kb=None, mover=1, is_vdm=False):
        if size_kb is None:
            # default to 2 MB
            size_kb = 2 * 1024

        pool = storops.vnx.resource.nas_pool.VNXNasPool.get_id(pool)
        mover = storops.vnx.resource.mover.VNXMover.get_id(mover)
        resp = cli.create_filesystem(name, size_kb, pool, mover, is_vdm)
        resp.raise_if_err()
        return VNXFileSystem(name, cli=cli)

    def create_snap(self, name, pool=None):
        if pool is None and self.pools:
            pool = self.pools[0]
        return VNXFsSnap.create(cli=self._cli, name=name, fs=self, pool=pool)

    def delete(self):
        resp = self._cli.delete_filesystem(self.get_fs_id())
        resp.raise_if_err()
        return resp

    def extend(self, new_size, pool=None):
        if pool is None and self.pools:
            pool = self.pools[0]
        pool_id = storops.vnx.resource.nas_pool.VNXNasPool.get_id(pool)
        fs_id = self.get_fs_id()
        delta_size = new_size - self.size
        resp = self._cli.extend_fs(fs_id, delta_size, pool_id)
        resp.raise_if_err()
        return resp

    def create_from_snapshot(self, name, snap_name, source_fs_name, pool_name,
                             mover_name, connect_id):
        # todo: normalize this function and add tests
        create_fs_cmd = [
            'env', 'NAS_DB=/nas', '/nas/bin/nas_fs',
            '-name', name,
            '-type', 'uxfs',
            '-create',
            'samesize=' + source_fs_name,
            'pool=%s' % pool_name,
            'storage=SINGLE',
            'worm=off',
            '-thin', 'no',
            '-option', 'slice=y',
        ]

        self._execute_cmd(create_fs_cmd)

        ro_mount_cmd = [
            'env', 'NAS_DB=/nas', '/nas/bin/server_mount', mover_name,
            '-option', 'ro',
            name,
            '/%s' % name,
        ]
        self._execute_cmd(ro_mount_cmd)

        session_name = name + ':' + snap_name
        copy_ckpt_cmd = [
            'env', 'NAS_DB=/nas', '/nas/bin/nas_copy',
            '-name', session_name[0:63],
            '-source', '-ckpt', snap_name,
            '-destination', '-fs', name,
            '-interconnect',
            'id=%s' % connect_id,
            '-overwrite_destination',
            '-full_copy',
        ]

        try:
            self._execute_cmd(copy_ckpt_cmd, check_exit_code=True)
        except SSHExecutionError as expt:
            message = (("Failed to copy content from snapshot %(snap)s to "
                        "file system %(filesystem)s. Reason: %(err)s.") %
                       {'snap': snap_name,
                        'filesystem': name,
                        'err': six.text_type(expt)})
            LOG.error(message)

        # When an error happens during nas_copy, we need to continue
        # deleting the checkpoint of the target file system if it exists.
        query_fs_cmd = [
            'env', 'NAS_DB=/nas', '/nas/bin/nas_fs',
            '-info', name,
        ]
        out, err = self._execute_cmd(query_fs_cmd)
        re_ckpts = r'ckpts\s*=\s*(.*)\s*'
        m = re.search(re_ckpts, out)
        if m is not None:
            ckpts = m.group(1)
            for ckpt in re.split(',', ckpts):
                umount_ckpt_cmd = [
                    'env', 'NAS_DB=/nas',
                    '/nas/bin/server_umount', mover_name,
                    '-perm', ckpt,
                ]
                self._execute_cmd(umount_ckpt_cmd)
                delete_ckpt_cmd = [
                    'env', 'NAS_DB=/nas', '/nas/bin/nas_fs',
                    '-delete', ckpt,
                    '-Force',
                ]
                self._execute_cmd(delete_ckpt_cmd)

        rw_mount_cmd = [
            'env', 'NAS_DB=/nas', '/nas/bin/server_mount', mover_name,
            '-option', 'rw',
            name,
            '/%s' % name,
        ]
        self._execute_cmd(rw_mount_cmd)

        filesystem = {
            'name': name,
        }
        self.filesystem_map[name] = self.resource_class(self, filesystem)

        return self.filesystem_map[name]
