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

from tobiko.openstack import neutron
from tobiko.tests.unit import openstack


class NeutronExtensionTest(openstack.OpenstackTest):

    extensions = ['ext-1', 'ext-2', 'ext-3']

    def setUp(self):
        super(NeutronExtensionTest, self).setUp()
        self.client = self.patch_get_neutron_client().return_value
        self.client.list_extensions.return_value = {
            'extensions': [{'alias': e} for e in self.extensions]}

    def test_get_networking_extensions(self):
        result = neutron.get_networking_extensions()
        self.assertEqual(frozenset(self.extensions), result)

    def test_missing_networking_extensions(self):
        result = neutron.missing_networking_extensions(
            'ext-2', 'ext-4', 'ext-0')
        self.assertEqual(['ext-0', 'ext-4'], result)

    def test_has_networking_extensions(self):
        self.assertTrue(neutron.has_networking_extensions(*self.extensions))
        self.assertFalse(neutron.has_networking_extensions('ext-1', 'ext-4'))

    def test_skip_if_networking_extensions_when_missing(self):
        ex = self.assertRaises(
            self.skipException,
            self._test_skip_if_networking_extensions_when_missing)
        self.assertEqual("missing networking extensions: ['ext-4']", str(ex))

    @neutron.skip_if_missing_networking_extensions('ext-1', 'ext-4')
    def _test_skip_if_networking_extensions_when_missing(self):
        self.fail('Not skipped')

    def test_skip_if_networking_extensions_when_not_missing(self):
        ex = self.assertRaises(
            self.failureException,
            self._test_skip_if_networking_extensions_when_not_missing)
        self.assertEqual('OK', str(ex))

    @neutron.skip_if_missing_networking_extensions('ext-1', 'ext-2')
    def _test_skip_if_networking_extensions_when_not_missing(self):
        self.fail('OK')
