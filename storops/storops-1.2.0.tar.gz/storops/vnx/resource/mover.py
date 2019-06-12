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

import storops.vnx.resource.nfs_share

from storops.lib.common import check_int
from storops.vnx.enums import VNXPortType
from storops.vnx.resource import VNXCliResourceList, VNXResource

__author__ = 'Jay Xu'

LOG = logging.getLogger(__name__)


class VNXMoverRefList(VNXCliResourceList):
    @classmethod
    def get_resource_class(cls):
        return VNXMoverRef

    def _get_raw_resource(self):
        return self._cli.get_mover(full=False)


class VNXMoverRef(VNXResource):
    _full_prop = False

    def __init__(self, name=None, mover_id=None, cli=None):
        super(VNXMoverRef, self).__init__()
        self._name = name
        self._mover_id = mover_id
        self._cli = cli

        # cache for members
        self._host = None

    def update(self, data=None):
        super(VNXMoverRef, self).update(data)

    @property
    def is_vdm(self):
        return False

    def get_mover_id(self):
        if self._mover_id is not None:
            ret = self._mover_id
        else:
            ret = self.mover_id
        return ret

    def _get_raw_resource(self):
        if self._mover_id is not None:
            resp = self._cli.get_mover(mover_id=self._mover_id,
                                       full=self._full_prop)
        elif self._name is not None:
            resp = self._cli.get_mover(full=self._full_prop)
            resp.filter_object(name=self._name)
        else:
            raise ValueError('mover_id or name should be supplied.')
        return resp

    @classmethod
    def get_id(cls, item):
        if isinstance(item, VNXMoverRef):
            ret = item.get_mover_id()
        else:
            ret = check_int(item)
        return ret

    def create_dns(self, domain_name, ip):
        if isinstance(ip, (list, tuple)):
            ip = ' '.join(ip)
        resp = self._cli.create_dns_domain(self.get_mover_id(), domain_name,
                                           ip)
        resp.raise_if_err()
        return resp

    def delete_dns(self, domain_name):
        resp = self._cli.delete_dns_domain(self.get_mover_id(), domain_name)
        resp.raise_if_err()
        return resp

    @property
    def host(self):
        if self._host is None:
            self._host = VNXMoverHost(host_id=self.host_id, cli=self._cli)
        return self._host

    @property
    def physical_devices(self):
        return self.host.physical_device

    @property
    def fc_devices(self):
        return [device for device in self.physical_devices
                if device.type == VNXPortType.FC]

    @property
    def ethernet_devices(self):
        return [device for device in self.physical_devices
                if device.type == VNXPortType.ETHERNET]

    def get_interconnect_id(self, source=None, destination=None):
        if source is None:
            source = self.name
        if destination is None:
            destination = self.name

        out = self._cli.get_mover_interconnect_id_list()

        for line in out.strip().split('\n'):
            _id, name, src, dest_system, dest = line.strip().split()
            if src == source and dest == destination:
                conn_id = check_int(_id)
                break
        else:
            conn_id = None

        return conn_id

    def create_nfs_share(self, path, ro=False, host_config=None):
        share_clz = storops.vnx.resource.nfs_share.VNXNfsShare
        return share_clz.create(self._cli, self, path, ro, host_config)


class VNXMoverList(VNXCliResourceList):
    @classmethod
    def get_resource_class(cls):
        return VNXMover

    def _get_raw_resource(self):
        return self._cli.get_mover()


class VNXMover(VNXMoverRef):
    _full_prop = True

    @staticmethod
    def get(cli, name=None, mover_id=None):
        if name is not None or mover_id is not None:
            ret = VNXMover(name=name, mover_id=mover_id, cli=cli)
        else:
            ret = VNXMoverList(cli=cli)
        return ret

    @property
    def interfaces(self):
        ret = []
        for i in self.mover_interfaces:
            i._mover = self
            i._cli = self._cli
            ret.append(i)
        return ret

    def create_interface(self, device, ip, net_mask, vlan_id=0, name=None):
        mover_id = self.get_mover_id()
        if hasattr(device, 'name'):
            device = device.name
        resp = self._cli.create_mover_interface(
            mover_id, device, ip, net_mask, vlan_id, name)
        resp.raise_if_err()
        return VNXMoverInterface(mover=self, cli=self._cli, ip=ip)

    def delete_interface(self, ip):
        interface = next(i for i in self.interfaces if i.ip_addr == ip)
        return interface.delete()


class VNXMoverInterfaceList(VNXCliResourceList):
    @classmethod
    def get_resource_class(cls):
        return VNXMoverInterface


class VNXMoverInterface(VNXResource):
    def __init__(self, mover=None, ip=None, cli=None):
        super(VNXMoverInterface, self).__init__()
        self._cli = cli
        self._mover = mover
        self._ip = ip

    def _get_raw_resource(self):
        self._mover.update()
        interface = next(i for i in self._mover.interfaces
                         if i.ip_addr == self._ip)
        return interface.parsed_resource

    def get_ip(self):
        if self._ip is not None:
            ret = self._ip
        else:
            ret = self.ip_addr
        return ret

    def delete(self):
        mover_id = self._mover.get_mover_id()
        resp = self._cli.delete_mover_interface(mover_id, self.get_ip())
        resp.raise_if_err()
        return resp


class VNXMoverLogicalNetworkDeviceList(VNXCliResourceList):
    @classmethod
    def get_resource_class(cls):
        return VNXMoverLogicalNetworkDevice


class VNXMoverLogicalNetworkDevice(VNXResource):
    pass


class VNXMoverRouteList(VNXCliResourceList):
    @classmethod
    def get_resource_class(cls):
        return VNXMoverRoute


class VNXMoverRoute(VNXResource):
    pass


class VNXMoverDeduplicationSettings(VNXResource):
    pass


class VNXMoverHostList(VNXCliResourceList):
    @classmethod
    def get_resource_class(cls):
        return VNXMoverHost

    def _get_raw_resource(self):
        return self._cli.get_mover_host()


class VNXMoverHost(VNXResource):
    def __init__(self, host_id=None, cli=None):
        super(VNXMoverHost, self).__init__()
        self._host_id = host_id
        self._cli = cli

    def _get_raw_resource(self):
        return self._cli.get_mover_host(self._host_id)


class VNXMoverMotherboard(VNXResource):
    pass


class VNXMoverPhysicalDeviceList(VNXCliResourceList):
    @classmethod
    def get_resource_class(cls):
        return VNXMoverPhysicalDevice


class VNXMoverPhysicalDevice(VNXResource):
    @property
    def is_internal(self):
        ret = False
        if self.name:
            header = self.name[:3]
            ret = header in ('mge', 'fxg', 'tks', 'fsn')
        return ret
