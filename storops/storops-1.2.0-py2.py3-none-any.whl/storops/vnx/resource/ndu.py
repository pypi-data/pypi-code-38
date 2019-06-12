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

from storops.vnx.resource import VNXCliResourceList
from storops.vnx.resource import VNXCliResource

__author__ = 'Cedric Zhuang'


class VNXNduList(VNXCliResourceList):
    @classmethod
    def get_resource_class(cls):
        return VNXNdu

    def _get_raw_resource(self):
        return self._cli.get_ndu(poll=self.poll)

    def _check_package(self, name):
        for ndu in self:
            if ndu.name == name:
                ret = VNXNdu.is_enabled(ndu)
                break
        else:
            ret = False
        return ret

    def is_dedup_enabled(self):
        return self._check_package(VNXNdu.DEDUP)

    def is_compression_enabled(self):
        return self._check_package(VNXNdu.COMPRESSION)

    def is_auto_tiering_enabled(self):
        return self._check_package(VNXNdu.AUTO_TIERING)

    def is_mirror_view_async_enabled(self):
        return self._check_package(VNXNdu.MIRROR_VIEW_ASYNC)

    def is_mirror_view_sync_enabled(self):
        return self._check_package(VNXNdu.MIRROR_VIEW_SYNC)

    def is_mirror_view_enabled(self):
        return (self.is_mirror_view_async_enabled() and
                self.is_mirror_view_sync_enabled())

    def is_sancopy_enabled(self):
        return self._check_package(VNXNdu.SANCOPY)

    def is_thin_enabled(self):
        return self._check_package(VNXNdu.THIN)

    def is_snap_enabled(self):
        return self._check_package(VNXNdu.SNAP)

    def is_fast_cache_enabled(self):
        return self._check_package(VNXNdu.FAST_CACHE)


class VNXNdu(VNXCliResource):
    DEDUP = '-Deduplication'
    COMPRESSION = '-Compression'
    AUTO_TIERING = '-FAST'
    MIRROR_VIEW_ASYNC = '-MirrorView/A'
    MIRROR_VIEW_SYNC = '-MirrorView/S'
    SANCOPY = '-SANCopy'
    THIN = '-ThinProvisioning'
    SNAP = '-VNXSnapshots'
    FAST_CACHE = '-FASTCache'

    def __init__(self, name=None, cli=None):
        super(VNXNdu, self).__init__()
        self._cli = cli
        self._name = name

    def _get_raw_resource(self):
        return self._cli.get_ndu(name=self._name, poll=self.poll)

    @staticmethod
    def is_enabled(ndu):
        return ndu.existed and ndu.active_state and not ndu.commit_required

    @classmethod
    def _check_package(cls, cli, name):
        ndu = VNXNdu(name, cli)
        ndu.with_no_poll()
        return cls.is_enabled(ndu)

    @classmethod
    def is_dedup_enabled(cls, cli):
        return cls._check_package(cli, cls.DEDUP)

    @classmethod
    def is_compression_enabled(cls, cli):
        return cls._check_package(cli, cls.COMPRESSION)

    @classmethod
    def is_auto_tiering_enabled(cls, cli):
        return cls._check_package(cli, cls.AUTO_TIERING)

    @classmethod
    def is_mirror_view_async_enabled(cls, cli):
        return cls._check_package(cli, cls.MIRROR_VIEW_ASYNC)

    @classmethod
    def is_mirror_view_sync_enabled(cls, cli):
        return cls._check_package(cli, cls.MIRROR_VIEW_SYNC)

    @classmethod
    def is_mirror_view_enabled(cls, cli):
        return (cls.is_mirror_view_async_enabled(
            cli) and cls.is_mirror_view_sync_enabled(cli))

    @classmethod
    def is_sancopy_enabled(cls, cli):
        return cls._check_package(cli, cls.SANCOPY)

    @classmethod
    def is_thin_enabled(cls, cli):
        return cls._check_package(cli, cls.THIN)

    @classmethod
    def is_snap_enabled(cls, cli):
        return cls._check_package(cli, cls.SNAP)

    @classmethod
    def is_fast_cache_enabled(cls, cli):
        return cls._check_package(cli, cls.FAST_CACHE)

    @classmethod
    def get(cls, cli, name=None):
        if name is None:
            ret = VNXNduList(cli)
        else:
            ret = VNXNdu(name, cli)
        return ret
