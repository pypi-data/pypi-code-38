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

from storops.exception import check_nas_cmd_error
from storops.vnx.enums import VNXShareType
from storops.vnx.resource.mover import VNXMover
from storops.vnx.resource import VNXResource, VNXCliResourceList

__author__ = 'Cedric Zhuang'

LOG = logging.getLogger(__name__)


class VNXVdmInterface(object):
    def __init__(self, name, share_type):
        self.name = name
        if 'vdm' in share_type:
            share_type = 'nfs'
        self.share_type = VNXShareType.parse(share_type)


class VNXVdmList(VNXCliResourceList):
    @classmethod
    def get_resource_class(cls):
        return VNXVdm

    def _get_raw_resource(self):
        return self._cli.get_vdm()


class VNXVdm(VNXResource):
    def __init__(self, name=None, vdm_id=None, cli=None):
        super(VNXVdm, self).__init__()
        self._name = name
        self._vdm_id = vdm_id
        self._cli = cli

    def get_vdm_id(self):
        if self._vdm_id is not None:
            ret = self._vdm_id
        else:
            ret = self.vdm_id
        return ret

    def get_mover_id(self):
        return self.get_vdm_id()

    @staticmethod
    def get(cli, name=None, vdm_id=None):
        if name is not None or vdm_id is not None:
            ret = VNXVdm(name=name, vdm_id=vdm_id, cli=cli)
        else:
            ret = VNXVdmList(cli)
        return ret

    @property
    def is_vdm(self):
        return True

    def _get_raw_resource(self):
        if self._vdm_id is not None:
            resp = self._cli.get_vdm(self._vdm_id)
        else:
            resp = self._cli.get_vdm()
            resp.filter_object(name=self._name)
        return resp

    @classmethod
    def create(cls, cli, mover_id, name, pool_id=None):
        resp = cli.create_vdm(mover_id, name, pool_id)
        resp.raise_if_err()
        return VNXVdm(name=name, cli=cli)

    def delete(self):
        resp = self._cli.delete_vdm(self.get_vdm_id())
        resp.raise_if_err()
        return resp

    def get_interfaces(self):
        ret = []

        re_pattern = (r'Interfaces to services mapping:'
                      r'\s*(?P<interfaces>(\s*interface=.*)*)')

        out = self._cli.get_dm_interfaces(name=self._get_name(),
                                          is_vdm=True)

        m = re.search(re_pattern, out)
        if m:
            if_list = m.group('interfaces').split('\n')
            for i in if_list:
                m_if = re.search(r'\s*interface=(?P<if>.*)\s*:'
                                 r'\s*(?P<type>.*)\s*', i)
                if m_if:
                    if_name = m_if.group('if').strip()
                    share_type = m_if.group('type')
                    ret.append(VNXVdmInterface(if_name, share_type))
        return ret

    @property
    def mover(self):
        return VNXMover(mover_id=self.mover_id, cli=self._cli)

    def create_interface(self, device, ip, net_mask, vlan_id=0, name=None):
        return self.mover.create_interface(device, ip, net_mask, vlan_id, name)

    def delete_interface(self, ip):
        return self.mover.delete_interface(ip)

    @property
    def physical_devices(self):
        return self.mover.physical_device

    @property
    def fc_devices(self):
        return self.mover.fc_devices

    @property
    def ethernet_devices(self):
        return self.mover.ethernet_devices

    def attach_nfs_interface(self, if_name):
        out = self._cli.attach_nfs_interface(
            if_name, vdm_name=self._get_name())
        check_nas_cmd_error(out)
        return out

    def detach_nfs_interface(self, if_name):
        out = self._cli.detach_nfs_interface(
            if_name, vdm_name=self._get_name())
        check_nas_cmd_error(out)
        return out
