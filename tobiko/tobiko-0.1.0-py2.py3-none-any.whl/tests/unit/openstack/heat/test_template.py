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

import os

from tobiko.openstack import heat
from tobiko.tests.unit import openstack


class GetHeatTemplateTest(openstack.OpenstackTest):

    template_dirs = [os.path.dirname(__file__)]
    template_file = 'my-stack.yaml'

    def test_get_template(self, template_file=None, template_dirs=None):
        template_file = template_file or self.template_file
        template_dirs = template_dirs or self.template_dirs
        template = heat.get_heat_template(template_file=template_file,
                                          template_dirs=template_dirs)
        self.assertIsInstance(template, heat.HeatTemplate)
        self.assertIsInstance(template.template, dict)
        self.assertEqual(
            os.path.join(os.path.dirname(__file__), template_file),
            template.file)
