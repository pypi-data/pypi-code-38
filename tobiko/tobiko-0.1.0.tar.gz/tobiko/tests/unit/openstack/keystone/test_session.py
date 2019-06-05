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

from keystoneauth1 import session as keystonesession
import mock

import tobiko
from tobiko.openstack import keystone
from tobiko.tests.unit import openstack


CREDENTIALS = keystone.keystone_credentials(
    api_version=3,
    auth_url='http://127.0.0.1:4000/identiy/v3',
    username='demo',
    project_name='demo',
    password='this is a secret',
    user_domain_name='Default',
    project_domain_name='Default')


class CredentialsFixture(tobiko.SharedFixture):

    credentials = None

    def setup_fixture(self):
        self.credentials = CREDENTIALS


class DefaultCredentialsFixture(tobiko.SharedFixture):

    credentials = None

    def setup_fixture(self):
        self.credentials = DEFAULT_CREDENTIALS


DEFAULT_CREDENTIALS = keystone.keystone_credentials(
    api_version=2,
    auth_url='http://127.0.0.1:5000/identiy/v2.0',
    username='admin',
    project_name='admin',
    password='this is a secret')


class CheckSessionCredentialsMixin(object):

    def check_session_credentials(self, session, credentials):
        if credentials:
            if tobiko.is_fixture(credentials):
                self.assertIsNone(session.credentials)
                self.assertIs(credentials, session.credentials_fixture)
            else:
                self.assertIs(credentials, session.credentials)
                self.assertIsNone(session.credentials_fixture)
        else:
            self.assertIsNone(session.credentials)
            self.assertIsNone(session.credentials_fixture)


class KeystoneSessionFixtureTest(CheckSessionCredentialsMixin,
                                 openstack.OpenstackTest):

    default_credentials_fixture = (
        'tobiko.openstack.keystone._credentials.'
        'DefaultKeystoneCredentialsFixture')

    def setUp(self):
        super(KeystoneSessionFixtureTest, self).setUp()
        from tobiko.openstack.keystone import _credentials

        tobiko.remove_fixture(self.default_credentials_fixture)
        self.patch(_credentials, 'DefaultKeystoneCredentialsFixture',
                   DefaultCredentialsFixture)

    def test_init(self, credentials=None):
        session = keystone.KeystoneSessionFixture(credentials=credentials)
        self.check_session_credentials(session=session,
                                       credentials=credentials)

    def test_init_with_credentials(self):
        self.test_init(credentials=CREDENTIALS)

    def test_init_with_credentials_fixture(self):
        self.test_init(credentials=CredentialsFixture())

    def test_init_with_credentials_fixture_type(self):
        self.test_init(credentials=CredentialsFixture)

    def test_setup(self, credentials=None):
        session = keystone.KeystoneSessionFixture(credentials=credentials)
        session.setUp()
        if credentials:
            if tobiko.is_fixture(credentials):
                if inspect.isclass(credentials):
                    credentials = tobiko.get_fixture(credentials)
                self.assertIs(credentials.credentials, session.credentials)
            else:
                self.assertIs(credentials, session.credentials)
        else:
            self.assertEqual(DEFAULT_CREDENTIALS, session.credentials)

    def test_setup_with_credentials(self):
        self.test_setup(credentials=CREDENTIALS)

    def test_setup_with_credentials_fixture(self):
        self.test_setup(credentials=CredentialsFixture())

    def test_setup_with_credentials_fixture_type(self):
        self.test_setup(credentials=CredentialsFixture)


class KeystoneSessionManagerTest(CheckSessionCredentialsMixin,
                                 openstack.OpenstackTest):

    def test_init(self):
        manager = keystone.KeystoneSessionManager()

        self.assertTrue(manager)

    def test_get_session(self, credentials=None, shared=True):
        manager = keystone.KeystoneSessionManager()
        session = manager.get_session(credentials=credentials,
                                      shared=shared)
        self.assertIsInstance(session, keystone.KeystoneSessionFixture)
        self.check_session_credentials(session=session,
                                       credentials=credentials)
        if shared:
            self.assertIs(session, manager.get_session(
                credentials=credentials))
        else:
            self.assertIsNot(session, manager.get_session(
                credentials=credentials))

    def test_get_session_with_credentials(self):
        self.test_get_session(credentials=CREDENTIALS)

    def test_get_session_with_not_shared(self):
        self.test_get_session(shared=False)

    def test_get_session_with_credentials_fixture(self):
        self.test_get_session(credentials=CredentialsFixture())

    def test_get_session_with_credentials_fixture_type(self):
        self.test_get_session(credentials=CredentialsFixture)

    def test_get_session_with_init_session(self):
        mock_session = mock.MagicMock(specs=keystone.KeystoneSessionFixture)
        init_session = mock.MagicMock(return_value=mock_session)
        manager = keystone.KeystoneSessionManager()
        session = manager.get_session(credentials=CREDENTIALS,
                                      init_session=init_session)
        self.assertIs(mock_session, session)
        init_session.assert_called_once_with(credentials=CREDENTIALS)


class GetKeystomeSessionTest(openstack.OpenstackTest):

    def test_get_keystone_session(self, credentials=None, shared=True):
        session1 = keystone.get_keystone_session(credentials=credentials,
                                                 shared=shared)
        session2 = keystone.get_keystone_session(credentials=credentials,
                                                 shared=shared)
        if shared:
            self.assertIs(session1, session2)
        else:
            self.assertIsNot(session1, session2)
        self.assertIsInstance(session1, keystonesession.Session)
        self.assertIsInstance(session2, keystonesession.Session)

    def test_get_keystone_session_with_not_shared(self):
        self.test_get_keystone_session(shared=False)

    def test_get_keystone_session_with_credentials(self):
        credentials = keystone.default_keystone_credentials()
        self.test_get_keystone_session(credentials=credentials)
