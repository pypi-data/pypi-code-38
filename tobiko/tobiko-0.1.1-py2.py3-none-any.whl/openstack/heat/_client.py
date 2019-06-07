# Copyright 2019 Red Hat
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
from __future__ import absolute_import

from heatclient import client as heatclient

from tobiko.openstack import _client


class HeatClientFixture(_client.OpenstackClientFixture):

    def init_client(self, session):
        return heatclient.Client(
            '1', session=session, endpoint_type='public',
            service_type='orchestration')


CLIENTS = _client.OpenstackClientManager(init_client=HeatClientFixture)


def get_heat_client(session=None, shared=True, init_client=None,
                    manager=None):
    manager = manager or CLIENTS
    client = manager.get_client(session=session, shared=shared,
                                init_client=init_client)
    client.setUp()
    return client.client
