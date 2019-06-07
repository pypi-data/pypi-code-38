# Copyright (c) 2019 Red Hat
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
from __future__ import absolute_import

import inspect

import mock

import tobiko
from tobiko.openstack import _client
from tobiko.openstack import keystone
from tobiko.tests.unit import openstack


CLIENT = object()


class ClientFixture(_client.OpenstackClientFixture):

    def init_client(self, session=None):
        return CLIENT


SESSION = object()

DEFAULT_SESSION = object()


class SessionFixture(tobiko.SharedFixture):

    session = None

    def setup_fixture(self):
        self.session = SESSION


class OpenstackClientFixtureTest(openstack.OpenstackTest):

    def create_client(self, session=None):
        return ClientFixture(session=session)

    def test_init(self, session=None):
        client = self.create_client(session=session)
        self.check_client_session(client=client, session=session)

    def test_init_with_credentials(self):
        self.test_init(session=SESSION)

    def test_init_with_credentials_fixture(self):
        self.test_init(session=keystone.KeystoneSessionFixture())

    def test_init_with_credentials_fixture_type(self):
        self.test_init(session=keystone.KeystoneSessionFixture)

    def test_setup(self, session=None):
        client = self.create_client(session=session)
        client.setUp()
        if session:
            if tobiko.is_fixture(session):
                if inspect.isclass(session):
                    session = tobiko.get_fixture(session)
                self.assertIs(session.session, client.session)
            else:
                self.assertIs(session, client.session)
        else:
            self.assertIs(keystone.get_keystone_session(), client.session)

    def test_setup_with_session(self):
        self.test_setup(session=SESSION)

    def test_setup_with_session_fixture(self):
        self.test_setup(session=SessionFixture())

    def test_setup_with_session_fixture_type(self):
        self.test_setup(session=SessionFixture)

    def check_client_session(self, client, session):
        if session:
            if tobiko.is_fixture(session):
                self.assertIsNone(client.session)
                self.assertIs(session, client.session_fixture)
            else:
                self.assertIs(session, client.session)
                self.assertIsNone(client.session_fixture)
        else:
            self.assertIsNone(client.session)
            self.assertIsNone(client.session_fixture)


class OpenstackClientManagerTest(openstack.OpenstackTest):

    def setUp(self):
        super(OpenstackClientManagerTest, self).setUp()
        self.patch(keystone, 'get_keystone_session',
                   return_value=DEFAULT_SESSION)

    def test_init(self, init_client=None):
        manager = _client.OpenstackClientManager(init_client=init_client)
        self.assertIs(init_client, manager.init_client)

    def test_init_with_init_client(self):
        self.test_init(init_client=ClientFixture)

    def test_get_client(self, session=None, shared=True):
        default_init_client = mock.MagicMock(side_effect=ClientFixture)
        manager = _client.OpenstackClientManager(
            init_client=default_init_client)
        client1 = manager.get_client(session=session, shared=shared)
        client2 = manager.get_client(session=session, shared=shared)
        if shared:
            self.assertIs(client1, client2)
            default_init_client.assert_called_once_with(
                session=(session or DEFAULT_SESSION))
        else:
            self.assertIsNot(client1, client2)
            default_init_client.assert_has_calls(
                [mock.call(session=(session or DEFAULT_SESSION))] * 2,
                any_order=True)

    def test_get_client_with_not_shared(self):
        self.test_get_client(shared=False)

    def test_get_client_with_session(self):
        self.test_get_client(session=SESSION)

    def test_get_client_with_session_fixture(self):
        self.test_get_client(session=SessionFixture())

    def test_get_client_with_session_fixture_type(self):
        self.test_get_client(session=SessionFixture)

    def test_get_client_with_init_client(self):
        init_client = mock.MagicMock(return_value=CLIENT)
        manager = _client.OpenstackClientManager()
        client = manager.get_client(session=SESSION,
                                    init_client=init_client)
        self.assertIs(CLIENT, client)
        init_client.assert_called_once_with(session=SESSION)
