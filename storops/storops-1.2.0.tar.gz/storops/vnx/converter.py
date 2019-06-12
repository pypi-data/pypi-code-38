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

from storops.lib.common import is_valid
from storops.lib.converter import to_int_arr, to_disk_indices, to_int
from storops.vnx.resource.disk import VNXDiskList
from storops.vnx.resource.lun import VNXLun, VNXLunList
from storops.vnx.resource.snap import VNXSnap

__author__ = 'Cedric Zhuang'


def id_to_lun(lun_id):
    if is_valid(lun_id):
        ret = VNXLun(lun_id=to_int(lun_id))
    else:
        ret = None
    return ret


def name_to_lun(name):
    if is_valid(name):
        ret = VNXLun(name=name)
    else:
        ret = None
    return ret


def name_to_snap(name):
    if is_valid(name):
        ret = VNXSnap(name=name)
    else:
        ret = None
    return ret


def ids_to_lun_list(id_list_str):
    ids = to_int_arr(id_list_str)
    if ids:
        ret = VNXLunList(lun_ids=ids)
    else:
        ret = tuple()
    return ret


def indices_to_disk_list(disk_indices_str):
    disk_indices = to_disk_indices(disk_indices_str)
    if disk_indices:
        ret = VNXDiskList(disk_indices=disk_indices)
    else:
        ret = tuple()
    return ret
