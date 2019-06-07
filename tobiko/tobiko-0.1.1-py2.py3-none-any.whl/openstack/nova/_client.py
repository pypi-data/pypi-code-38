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

from novaclient import client as novaclient

from tobiko.openstack import _client


class NovaClientFixture(_client.OpenstackClientFixture):

    def init_client(self, session):
        return novaclient.Client('2', session=session)


CLIENTS = _client.OpenstackClientManager(init_client=NovaClientFixture)


def get_nova_client(session=None, shared=True, init_client=None,
                    manager=None):
    manager = manager or CLIENTS
    client = manager.get_client(session=session, shared=shared,
                                init_client=init_client)
    client.setUp()
    return client.client
