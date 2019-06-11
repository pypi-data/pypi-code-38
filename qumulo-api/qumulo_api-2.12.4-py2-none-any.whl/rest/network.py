# Copyright (c) 2012 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import qumulo.lib.request as request

V1_SETTINGS_FIELDS = set((
    'assigned_by',
    'ip_ranges',
    'floating_ip_ranges',
    'netmask',
    'gateway',
    'gateway_ipv6',
    'dns_servers',
    'dns_search_domains',
    'mtu',
    'bonding_mode'
))

@request.request
def get_cluster_network_config(conninfo, credentials):
    method = "GET"
    uri = "/v1/network/settings"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def modify_cluster_network_config(conninfo, credentials, **kwargs):
    method = "PATCH"
    uri = "/v1/network/settings"

    config = { }

    for key, value in kwargs.items():
        assert key in V1_SETTINGS_FIELDS
        if value is not None:
            config[key] = value

    if set(kwargs.keys()) == V1_SETTINGS_FIELDS:
        method = "PUT"

    return request.rest_request(conninfo, credentials, method, uri, body=config)

@request.request
def list_network_status(conninfo, credentials):
    method = "GET"
    uri = "/v1/network/status/"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def get_network_status(conninfo, credentials, node):
    method = "GET"
    uri = "/v1/network/status/{}".format(node)

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def list_interfaces(conninfo, credentials):
    method = "GET"
    uri = "/v2/network/interfaces/"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def get_interface(conninfo, credentials, interface_id):
    method = "GET"
    uri = "/v2/network/interfaces/{}".format(interface_id)

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def list_networks(conninfo, credentials, interface_id):
    method = "GET"
    uri = "/v2/network/interfaces/{}/networks/".format(interface_id)

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def get_network(conninfo, credentials, interface_id, network_id):
    method = "GET"
    uri = "/v2/network/interfaces/{}/networks/{}".format(
        interface_id, network_id)

    return request.rest_request(conninfo, credentials, method, uri)

# Don't allow setting interface ID and name.
V2_INTERFACE_FIELDS = set((
    'bonding_mode',
    'default_gateway',
    'default_gateway_ipv6',
    'mtu',
))

@request.request
def modify_interface(conninfo, credentials, interface_id, **kwargs):
    # Always patch and don't allow setting interface ID and name.
    method = "PATCH"
    uri = "/v2/network/interfaces/{}".format(interface_id)

    config = { }

    for key, value in kwargs.items():
        assert key in V2_INTERFACE_FIELDS
        if value is not None:
            config[key] = value

    if set(config.keys()) == V2_INTERFACE_FIELDS:
        method = "PUT"

    return request.rest_request(conninfo, credentials, method, uri, body=config)

V2_NETWORK_FIELDS = set((
    'assigned_by',
    'name',
    'ip_ranges',
    'floating_ip_ranges',
    'netmask',
    'dns_servers',
    'dns_search_domains',
    'mtu',
    'vlan_id',
))

def populate_request_body(body, **kwargs):
    for key, value in kwargs.items():
        assert key in V2_NETWORK_FIELDS
        if value is not None:
            body[key] = value

    if 'floating_ip_ranges' in body and body['floating_ip_ranges'] == [ "" ]:
        body['floating_ip_ranges'] = []

    if 'dns_servers' in body and body['dns_servers'] == [ "" ]:
        body['dns_servers'] = []

    if 'dns_search_domains' in body and body['dns_search_domains'] == [ "" ]:
        body['dns_search_domains'] = []

    return body

@request.request
def add_network(conninfo, credentials, interface_id, **kwargs):
    method = "POST"
    uri = "/v2/network/interfaces/{}/networks/".format(interface_id)
    body = populate_request_body({}, **kwargs)

    return request.rest_request(conninfo, credentials, method, uri, body=body)

@request.request
def delete_network(conninfo, credentials, interface_id, network_id):
    method = "DELETE"
    uri = "/v2/network/interfaces/{}/networks/{}".format(interface_id,
        network_id)

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def modify_network(conninfo, credentials, interface_id, network_id, **kwargs):
    method = "PATCH"
    uri = "/v2/network/interfaces/{}/networks/{}".format(
        interface_id, network_id)

    body = populate_request_body({ "id": network_id }, **kwargs)
    return request.rest_request(conninfo, credentials, method, uri, body=body)

@request.request
def set_dhcp_network(
        conninfo, credentials, interface_id, network_id, name,
        floating_ip_ranges=None):

    method = "PUT"
    uri = "/v2/network/interfaces/{}/networks/{}".format(
        interface_id, network_id)

    dhcp_network_config = {
        "id": network_id,
        "assigned_by": "DHCP",
        "name": name,
        "floating_ip_ranges": floating_ip_ranges or [],
        # The rest of these fields are STATIC only and these are the defaults
        "ip_ranges": [],
        "netmask": "",
        "dns_servers": [],
        "dns_search_domains": [],
        "vlan_id": 0,
    }

    return request.rest_request(
        conninfo, credentials, method, uri, body=dhcp_network_config)

@request.request
def list_network_status_v2(conninfo, credentials, interface_id):
    method = "GET"
    uri = "/v2/network/interfaces/{}/status/".format(interface_id)

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def get_network_status_v2(conninfo, credentials, interface_id, node_id):
    method = "GET"
    uri = "/v2/network/interfaces/{}/status/{}".format(interface_id, node_id)

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def get_static_ip_allocation(conninfo, credentials,
        try_ranges=None, try_netmask=None, try_floating_ranges=None):
    method = "GET"
    uri = "/v1/network/static-ip-allocation"

    query_params = []

    if try_ranges:
        query_params.append("try={}".format(try_ranges))
    if try_netmask:
        query_params.append("netmask={}".format(try_netmask))
    if try_floating_ranges:
        query_params.append("floating={}".format(try_floating_ranges))

    if query_params:
        uri = uri + "?" + "&".join(query_params)

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def get_floating_ip_allocation(conninfo, credentials):
    method = "GET"
    uri = "/v1/network/floating-ip-allocation"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def connections(conninfo, credentials):
    method = "GET"
    uri = '/v2/network/connections/'

    return request.rest_request(conninfo, credentials, method, uri)
