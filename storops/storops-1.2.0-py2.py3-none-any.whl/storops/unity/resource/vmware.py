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

from storops.unity.resource import UnityResource, UnityResourceList

__author__ = 'Cedric Zhuang'


class UnityDataStore(UnityResource):
    pass


class UnityDataStoreList(UnityResourceList):
    @classmethod
    def get_resource_class(cls):
        return UnityDataStore


class UnityVmDisk(UnityResource):
    pass


class UnityVmDiskList(UnityResourceList):
    @classmethod
    def get_resource_class(cls):
        return UnityVmDisk


class UnityVm(UnityResource):
    pass


class UnityVmList(UnityResourceList):
    @classmethod
    def get_resource_class(cls):
        return UnityVm


class UnityVirtualVolume(UnityResource):
    pass


class UnityVirtualVolumeList(UnityResourceList):
    @classmethod
    def get_resource_class(cls):
        return UnityVirtualVolume


class UnityHostVvolDatastore(UnityResource):
    pass


class UnityHostVvolDatastoreList(UnityResourceList):
    @classmethod
    def get_resource_class(cls):
        return UnityHostVvolDatastore


class UnityCapabilityProfile(UnityResource):
    pass


class UnityCapabilityProfileList(UnityResourceList):
    @classmethod
    def get_resource_class(cls):
        return UnityCapabilityProfile


class UnityVirtualVolumeBinding(UnityResource):
    pass


class UnityVirtualVolumeBindingList(UnityResourceList):
    @classmethod
    def get_resource_class(cls):
        return UnityVirtualVolume


class UnityVmwarePE(UnityResource):
    pass


class UnityVmwarePEList(UnityResourceList):
    @classmethod
    def get_resource_class(cls):
        return UnityVmwarePE


class UnityVmwareNasPEServer(UnityResource):
    pass


class UnityVmwareNasPEServerList(UnityResourceList):
    @classmethod
    def get_resource_class(cls):
        return UnityVmwareNasPEServer
