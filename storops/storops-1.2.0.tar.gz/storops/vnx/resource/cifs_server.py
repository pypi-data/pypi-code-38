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

from storops.vnx.resource.mover import VNXMoverRefList
from storops.vnx.resource import VNXCliResourceList, VNXResource

__author__ = 'Jay Xu'

log = logging.getLogger(__name__)


class CifsDomain(object):
    def __init__(self, name, comp_name=None, user=None, password=None):
        self.name = name
        self.comp_name = comp_name
        self.user = user
        self.password = password


class VNXCifsServerList(VNXCliResourceList):
    def __init__(self, cli=None, mover_id=None, is_vdm=False):
        super(VNXCifsServerList, self).__init__(cli=cli)
        self.mover_id = mover_id
        self.is_vdm = is_vdm

    @classmethod
    def get_resource_class(cls):
        return VNXCifsServer

    def _get_raw_resource(self):
        return self._cli.get_cifs_server(mover_id=self.mover_id,
                                         is_vdm=self.is_vdm)


class VNXCifsServer(VNXResource):
    def __init__(self, name=None, cli=None):
        super(VNXCifsServer, self).__init__()
        self._name = name
        self._cli = cli

    def _get_raw_resource(self):
        return self._cli.get_cifs_server(name=self._name)

    @staticmethod
    def get(cli, name=None, mover_id=None, is_vdm=False):
        if name is not None:
            ret = VNXCifsServer(name=name, cli=cli)
        else:
            ret = VNXCifsServerList(cli=cli, mover_id=mover_id, is_vdm=is_vdm)
        return ret

    @staticmethod
    def create(cli, name, mover_id=None, is_vdm=False,
               workgroup=None, domain=None,
               interfaces=None, alias_name=None,
               local_admin_password=None):
        # default to first physical data mover
        if mover_id is None:
            movers = VNXMoverRefList(cli=cli)
            if not movers:
                raise ValueError('no data mover available.')
            mover_id = movers[0].mover_id
            is_vdm = False

        resp = cli.create_cifs_server(
            name=name, mover_id=mover_id, is_vdm=is_vdm,
            workgroup=workgroup, domain=domain,
            ip_list=interfaces, alias_name=alias_name,
            local_admin_password=local_admin_password)
        resp.raise_if_err()
        return VNXCifsServer(name=name, cli=cli)

    def delete(self, mover_id=None, is_vdm=False):
        if mover_id is None:
            mover_id = self.mover_id
            is_vdm = self.is_vdm
        resp = self._cli.delete_cifs_server(self._get_name(), mover_id, is_vdm)
        resp.raise_if_err()
        return resp

    def modify(self, name, mover_id=None, is_vdm=True,
               join_domain=False, username=None, password=None):
        if mover_id is None:
            mover_id = self.mover_id
            is_vdm = self.is_vdm
        resp = self._cli.modify_domain_cifs_server(
            name, mover_id, is_vdm, join_domain, username, password)
        resp.raise_if_err()
        return resp
