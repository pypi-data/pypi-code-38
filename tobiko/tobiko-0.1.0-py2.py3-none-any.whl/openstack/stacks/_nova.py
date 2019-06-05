# Copyright (c) 2019 Red Hat, Inc.
#
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

import six

from tobiko import config
from tobiko.openstack import heat
from tobiko.openstack.stacks import _hot


CONF = config.CONF


class NovaKeyPairStackFixture(heat.HeatStackFixture):
    template = _hot.heat_template_file('nova/key_pair.yaml')
    key_file = os.path.expanduser(CONF.tobiko.nova.key_file)
    public_key = None
    private_key = None

    def setup_fixture(self):
        self.read_keys()
        super(NovaKeyPairStackFixture, self).setup_fixture()

    def read_keys(self):
        with open(self.key_file, 'r') as fd:
            self.private_key = as_str(fd.read())
        with open(self.key_file + '.pub', 'r') as fd:
            self.public_key = as_str(fd.read())


def as_str(text):
    if isinstance(text, six.string_types):
        return text
    else:
        return text.decode()
