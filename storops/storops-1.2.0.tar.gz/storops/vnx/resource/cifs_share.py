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

import six

from storops.vnx.enums import VNXEnum
from storops.vnx.resource.mover import VNXMover
from storops.vnx.resource import VNXResource, VNXCliResourceList
from storops.vnx.resource.vdm import VNXVdm

__author__ = 'Jay Xu'

log = logging.getLogger(__name__)


class CifsAccessControl(VNXEnum):
    FULL = 'fullcontrol'
    READ = 'read'


class VNXCifsShareList(VNXCliResourceList):
    def __init__(self, cli=None, server_name=None, share_name=None,
                 mover=None):
        super(VNXCifsShareList, self).__init__(cli=cli)
        self._server_name = server_name
        self._share_name = share_name
        self._mover = mover

    @classmethod
    def get_resource_class(cls):
        return VNXCifsShare

    def _get_raw_resource(self):
        if self._mover is not None:
            mover_id = self._mover.get_mover_id()
            is_vdm = self._mover.is_vdm
        else:
            mover_id = None
            is_vdm = None

        return self._cli.get_cifs_share(
            server_name=self._server_name,
            share_name=self._share_name,
            mover_id=mover_id,
            is_vdm=is_vdm)


class VNXCifsShare(VNXResource):
    def __init__(self, name=None, mover=None, cli=None):
        super(VNXCifsShare, self).__init__()
        self._name = name
        self._mover = mover
        self._cli = cli

    def _get_raw_resource(self):
        if self._mover is None:
            raise ValueError('mover is not specified for this share.')

        return self._cli.get_cifs_share(
            share_name=self._name,
            server_name=None,
            mover_id=self._mover.get_mover_id(),
            is_vdm=self._mover.is_vdm)

    @staticmethod
    def get(cli, name=None, mover=None, server_name=None):
        if name is not None and mover is not None:
            ret = VNXCifsShare(name, mover, cli)
        else:
            ret = VNXCifsShareList(
                cli, server_name=server_name, share_name=name, mover=mover)
        return ret

    @staticmethod
    def create(cli, fs, server_name, mover, path=None):
        mover_id = mover.get_mover_id()
        is_vdm = mover.is_vdm
        if not isinstance(fs, six.string_types):
            name = fs.get_name()
        else:
            name = fs

        resp = cli.create_cifs_share(name, server_name, mover_id, is_vdm, path)
        resp.raise_if_err()
        return VNXCifsShare(name=name, mover=mover, cli=cli)

    @property
    def mover(self):
        if self._mover is not None:
            ret = self._mover
        elif self.is_vdm:
            ret = VNXVdm(vdm_id=self.mover_id, cli=self._cli)
        else:
            ret = VNXMover(mover_id=self.mover_id, cli=self._cli)
        return ret

    def delete(self, *server_names):
        if not server_names:
            server_names = self.cifs_server_names
        resp = self._cli.delete_cifs_share(
            self._get_name(), self.mover.get_mover_id(), server_names,
            self.mover.is_vdm)
        resp.raise_if_err()
        return resp

    def disable_share_access(self):
        self._cli.disable_cifs_share_access(self._get_name(),
                                            self.mover._get_name())

    def allow_share_access(self, user_name, domain,
                           access=CifsAccessControl.FULL):
        self._cli.allow_cifs_share_access(
            self.mover._get_name(), self._get_name(), user_name, domain,
            access)

    def deny_share_access(self, user_name, domain,
                          access=CifsAccessControl.FULL):
        self._cli.deny_cifs_share_access(
            self.mover._get_name(), self._get_name(), user_name, domain,
            access)
