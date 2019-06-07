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

SERVICES = ['openvswitch', 'tripleo_cinder_api', 'tripleo_cinder_api_cron',
            'tripleo_cinder_scheduler', 'tripleo_clustercheck',
            'tripleo_glance_api', 'tripleo_horizon']
CONTAINERS = ['neutron_ovs_agent', 'neutron_metadata_agent', 'neutron_api']
