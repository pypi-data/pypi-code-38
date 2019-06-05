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

import os

import tobiko
from tobiko import config
from tobiko.openstack import keystone
from tobiko.openstack.keystone import _credentials
from tobiko.tests.unit import openstack

V2_PARAMS = {
    'api_version': 2,
    'project_name': 'demo',
    'username': 'demo',
    'password': 'super-secret',
    'auth_url': 'http://10.0.0.1:5678/v2.0'}

V2_ENVIRON = {
    'OS_PROJECT_NAME': 'demo',
    'OS_USERNAME': 'demo',
    'OS_PASSWORD': 'super-secret',
    'OS_AUTH_URL': 'http://10.0.0.1:5678/v2.0'}

V2_ENVIRON_WITH_TENANT_NAME = {
    'OS_TENANT_NAME': 'demo',
    'OS_USERNAME': 'demo',
    'OS_PASSWORD': 'super-secret',
    'OS_AUTH_URL': 'http://10.0.0.1:5678/v2.0'}

V2_ENVIRON_WITH_VERSION = dict(V2_ENVIRON, OS_IDENTITY_API_VERSION='2')


V3_PARAMS = {
    'api_version': 3,
    'project_name': 'demo',
    'username': 'demo',
    'password': 'super-secret',
    'auth_url': 'http://10.0.0.1:5678/v3',
    'user_domain_name': 'Default',
    'project_domain_name': 'Default'}

V3_ENVIRON = {
    'OS_PROJECT_NAME': 'demo',
    'OS_USERNAME': 'demo',
    'OS_PASSWORD': 'super-secret',
    'OS_AUTH_URL': 'http://10.0.0.1:5678/v3',
    'OS_USER_DOMAIN_NAME': 'Default',
    'OS_PROJECT_DOMAIN_NAME': 'Default'}

V3_ENVIRON_WITH_VERSION = dict(V3_ENVIRON, OS_IDENTITY_API_VERSION='3')


def make_credentials(params, **kwargs):
    if kwargs:
        params = dict(params, **kwargs)
    return keystone.keystone_credentials(**params)


class KeystoneCredentialsTest(openstack.OpenstackTest):

    def test_validate_from_params_v2(self):
        credentials = make_credentials(V2_PARAMS)
        credentials.validate()
        self.assertEqual(V2_PARAMS, credentials.to_dict())
        self.assertEqual(
            "keystone_credentials(api_version=2, "
            "auth_url='http://10.0.0.1:5678/v2.0', username='demo', "
            "password='***', project_name='demo')",
            repr(credentials))

    def test_validate_from_params_v3(self):
        credentials = make_credentials(V3_PARAMS)
        credentials.validate()
        self.assertEqual(V3_PARAMS, credentials.to_dict())
        self.assertEqual(
            "keystone_credentials(api_version=3, "
            "auth_url='http://10.0.0.1:5678/v3', username='demo', "
            "password='***', project_name='demo', "
            "user_domain_name='Default', "
            "project_domain_name='Default')",
            repr(credentials))

    def test_validate_without_auth_url(self):
        credentials = make_credentials(V2_PARAMS, auth_url=None)
        self.assertRaises(keystone.InvalidKeystoneCredentials,
                          credentials.validate)

    def test_validate_without_username(self):
        credentials = make_credentials(V2_PARAMS, username=None)
        self.assertRaises(keystone.InvalidKeystoneCredentials,
                          credentials.validate)

    def test_validate_without_project_name(self):
        credentials = make_credentials(V2_PARAMS, project_name=None)
        self.assertRaises(keystone.InvalidKeystoneCredentials,
                          credentials.validate)

    def test_validate_without_password(self):
        credentials = make_credentials(V2_PARAMS, password=None)
        self.assertRaises(keystone.InvalidKeystoneCredentials,
                          credentials.validate)


class EnvironKeystoneCredentialsFixtureTest(openstack.OpenstackTest):

    def test_init(self):
        fixture = _credentials.EnvironKeystoneCredentialsFixture()
        self.assertIsNone(fixture.credentials)

    def test_setup_v2(self):
        self.patch(os, 'environ', V2_ENVIRON)
        fixture = _credentials.EnvironKeystoneCredentialsFixture()
        fixture.setUp()
        fixture.credentials.validate()
        self.assertEqual(V2_PARAMS, fixture.credentials.to_dict())

    def test_setup_v2_with_tenant_name(self):
        self.patch(os, 'environ', V2_ENVIRON_WITH_TENANT_NAME)
        fixture = _credentials.EnvironKeystoneCredentialsFixture()
        fixture.setUp()
        fixture.credentials.validate()
        self.assertEqual(V2_PARAMS, fixture.credentials.to_dict())

    def test_setup_v2_with_api_version(self):
        self.patch(os, 'environ', V2_ENVIRON_WITH_VERSION)
        fixture = _credentials.EnvironKeystoneCredentialsFixture()
        fixture.setUp()
        fixture.credentials.validate()
        self.assertEqual(V2_PARAMS, fixture.credentials.to_dict())

    def test_setup_v3(self):
        self.patch(os, 'environ', V3_ENVIRON)
        fixture = _credentials.EnvironKeystoneCredentialsFixture()
        fixture.setUp()
        fixture.credentials.validate()
        self.assertEqual(V3_PARAMS, fixture.credentials.to_dict())

    def test_setup_v3_without_api_version(self):
        self.patch(os, 'environ', V3_ENVIRON_WITH_VERSION)
        fixture = _credentials.EnvironKeystoneCredentialsFixture()
        fixture.setUp()
        fixture.credentials.validate()
        self.assertEqual(V3_PARAMS, fixture.credentials.to_dict())


class ConfigKeystoneCredentialsFixtureTest(openstack.OpenstackTest):

    def patch_config(self, params, **kwargs):
        credentials = make_credentials(params, **kwargs)
        return self.patch(config.CONF.tobiko, 'keystone', credentials)

    def test_init(self):
        fixture = _credentials.ConfigKeystoneCredentialsFixture()
        self.assertIsNone(fixture.credentials)

    def test_setup_v2(self):
        self.patch_config(V2_PARAMS, api_version=None)
        fixture = _credentials.ConfigKeystoneCredentialsFixture()
        fixture.setUp()
        fixture.credentials.validate()
        self.assertEqual(V2_PARAMS, fixture.credentials.to_dict())

    def test_setup_v2_with_api_version(self):
        self.patch_config(V2_PARAMS, api_version=2)
        fixture = _credentials.ConfigKeystoneCredentialsFixture()
        fixture.setUp()
        fixture.credentials.validate()
        self.assertEqual(V2_PARAMS, fixture.credentials.to_dict())

    def test_setup_v3(self):
        self.patch_config(V3_PARAMS, api_version=None)
        fixture = _credentials.ConfigKeystoneCredentialsFixture()
        fixture.setUp()
        fixture.credentials.validate()
        self.assertEqual(V3_PARAMS, fixture.credentials.to_dict())

    def test_setup_v3_with_api_version(self):
        self.patch_config(V3_PARAMS, api_version=3)
        fixture = _credentials.ConfigKeystoneCredentialsFixture()
        fixture.setUp()
        fixture.credentials.validate()
        self.assertEqual(V3_PARAMS, fixture.credentials.to_dict())


class DefaultKeystoneCredentialsFixtureTest(openstack.OpenstackTest):

    def setUp(self):
        super(DefaultKeystoneCredentialsFixtureTest, self).setUp()
        self.patch_config({})
        self.patch(os, 'environ', {})
        tobiko.remove_fixture(_credentials.ConfigKeystoneCredentialsFixture)
        tobiko.remove_fixture(_credentials.EnvironKeystoneCredentialsFixture)

    def patch_config(self, params, **kwargs):
        credentials = make_credentials(params, **kwargs)
        return self.patch(config.CONF.tobiko, 'keystone', credentials)

    def test_init(self):
        fixture = _credentials.DefaultKeystoneCredentialsFixture()
        self.assertIsNone(fixture.credentials)

    def test_setup_from_environ(self):
        self.patch(os, 'environ', V2_ENVIRON)
        fixture = _credentials.DefaultKeystoneCredentialsFixture()
        fixture.setUp()
        fixture.credentials.validate()
        self.assertEqual(V2_PARAMS, fixture.credentials.to_dict())

    def test_setup_from_config(self):
        self.patch_config(V2_PARAMS)
        fixture = _credentials.DefaultKeystoneCredentialsFixture()
        fixture.setUp()
        fixture.credentials.validate()
        self.assertEqual(V2_PARAMS, fixture.credentials.to_dict())

    def test_setup_from_environ_and_confif(self):
        self.patch(os, 'environ', V3_ENVIRON)
        self.patch_config(V2_PARAMS)
        fixture = _credentials.DefaultKeystoneCredentialsFixture()
        fixture.setUp()
        fixture.credentials.validate()
        self.assertEqual(V3_PARAMS, fixture.credentials.to_dict())
