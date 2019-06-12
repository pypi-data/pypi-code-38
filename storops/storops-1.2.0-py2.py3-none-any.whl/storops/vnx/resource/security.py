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

from storops.exception import raise_if_err, VNXSecurityException
from storops.vnx.resource import VNXCliResource, VNXCliResourceList

__author__ = 'Cedric Zhuang'


class VNXBlockUser(VNXCliResource):
    def __init__(self, name=None, cli=None):
        super(VNXBlockUser, self).__init__()
        self._cli = cli
        self._name = name

    @classmethod
    def get(cls, cli, name=None):
        if name is None:
            ret = VNXBlockUserList(cli=cli)
        else:
            ret = VNXBlockUser(name=name, cli=cli)
        return ret

    @classmethod
    def create(cls, cli, name, password, scope=None, role=None):
        out = cli.add_user(name, password, scope=scope, role=role)
        raise_if_err(out, default=VNXSecurityException)
        return VNXBlockUser(name=name, cli=cli)

    def delete(self):
        out = self._cli.delete_user(name=self._get_name(), scope=self.scope)
        raise_if_err(out, default=VNXSecurityException)

    def _get_raw_resource(self):
        return self._cli.list_user(name=self._name)


class VNXBlockUserList(VNXCliResourceList):
    @classmethod
    def get_resource_class(cls):
        return VNXBlockUser

    def _get_raw_resource(self):
        return self._cli.list_user()
