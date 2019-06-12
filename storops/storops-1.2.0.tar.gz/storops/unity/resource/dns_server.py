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

import storops.unity.resource.nas_server
from storops.unity.resource import UnityResource, UnityResourceList, \
    UnityAttributeResource

__author__ = 'Jay Xu'

LOG = logging.getLogger(__name__)


class UnityFileDnsServer(UnityResource):
    @classmethod
    def create(cls, cli, nas_server, domain, ip_list):
        clz = storops.unity.resource.nas_server.UnityNasServer
        nas_server = clz.get(cli, nas_server)

        resp = cli.post(cls().resource_class,
                        nasServer=nas_server,
                        domain=domain,
                        addresses=ip_list)
        resp.raise_if_err()
        return cls(_id=resp.resource_id, cli=cli)


class UnityFileDnsServerList(UnityResourceList):
    @classmethod
    def get_resource_class(cls):
        return UnityFileDnsServer


class UnityFileDNSServerSourceParameters(UnityAttributeResource):
    pass
