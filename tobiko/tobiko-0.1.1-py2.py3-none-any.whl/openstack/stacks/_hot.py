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

from tobiko.openstack import heat
from tobiko import config


CONF = config.CONF

TEMPLATE_DIRS = [os.path.dirname(__file__)]


def heat_template_file(template_file):
    """Fixture to load template files from templates directory

    Return fixtures to loads templates from
    'tobiko/tests/scenario/neutron/templates' directory
    """
    return heat.heat_template_file(template_file=template_file,
                                   template_dirs=TEMPLATE_DIRS)
