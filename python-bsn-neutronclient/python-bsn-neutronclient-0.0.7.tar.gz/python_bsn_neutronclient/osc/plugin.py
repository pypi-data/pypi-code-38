# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""OpenStackClient plugin for bsn neutron plugin."""

import logging
from osc_lib import utils

LOG = logging.getLogger(__name__)

DEFAULT_API_VERSION = '2.0'
API_VERSION_OPTION = 'os_network_api_version'
# NOTE(rtheis): API_NAME must NOT be set to 'network' since
# 'network' is owned by OSC!  The OSC 'network' client uses
# the OpenStack SDK.
API_NAME = 'bsn_neutronclient'
API_VERSIONS = {
    '2.0': 'python_bsn_neutronclient.v2_0.client.Client',
    '2': 'python_bsn_neutronclient.v2_0.client.Client',
}


def make_client(instance):
    """Returns a bsn neutron client."""
    bsn_neutron_client = utils.get_client_class(
        API_NAME,
        instance._api_version[API_NAME],
        API_VERSIONS)
    LOG.debug('Instantiating bsn neutron client: %s', bsn_neutron_client)

    client = bsn_neutron_client(session=instance.session,
                                region_name=instance.region_name,
                                endpoint_type=instance.interface,
                                insecure=not instance.verify,
                                ca_cert=instance.cacert)

    return client


def build_option_parser(parser):
    """Hook to add global options"""
    # OSC itself has an option for Network API version # and we refer to it.
    return parser
