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

@request.request
def list_nodes(conninfo, credentials):
    method = "GET"
    uri = "/v1/cluster/nodes/"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def list_node(conninfo, credentials, node):
    method = "GET"
    uri = "/v1/cluster/nodes/{}".format(node)

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def get_cluster_conf(conninfo, credentials):
    method = "GET"
    uri = "/v1/cluster/settings"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def put_cluster_conf(conninfo, credentials, cluster_name):
    method = "PUT"
    uri = "/v1/cluster/settings"

    config = {
        'cluster_name': str(cluster_name)
    }

    return request.rest_request(conninfo, credentials, method, uri,
        body=config)

@request.request
def set_ssl_certificate(conninfo, credentials, certificate, private_key):
    method = "PUT"
    uri = "/v2/cluster/settings/ssl/certificate"

    config = {
        'certificate': unicode(certificate),
        'private_key': unicode(private_key),
    }

    return request.rest_request(conninfo, credentials, method, uri, body=config)

@request.request
def set_ssl_ca_certificate(conninfo, credentials, ca_cert):
    method = "PUT"
    uri = "/v2/cluster/settings/ssl/ca-certificate"
    body = {
        "ca_certificate": unicode(ca_cert),
    }
    return request.rest_request(conninfo, credentials, method, uri, body=body)

@request.request
def get_ssl_ca_certificate(conninfo, credentials):
    method = "GET"
    uri = "/v2/cluster/settings/ssl/ca-certificate"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def delete_ssl_ca_certificate(conninfo, credentials):
    method = "DELETE"
    uri = "/v2/cluster/settings/ssl/ca-certificate"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def get_cluster_slots_status(conninfo, credentials):
    method = "GET"
    uri = "/v1/cluster/slots/"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def get_cluster_slot_status(conninfo, credentials, slot):
    method = "GET"
    uri = "/v1/cluster/slots/{}".format(slot)

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def get_restriper_status(conninfo, credentials):
    method = "GET"
    uri = "/v1/cluster/restriper/status"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def get_protection_status(conninfo, credentials):
    method = "GET"
    uri = "/v1/cluster/protection/status"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def set_node_identify_light(conninfo, credentials, node, light_visible):
    method = "POST"
    uri = "/v1/cluster/nodes/{}/identify".format(node)

    body = {'light_visible': light_visible}

    return request.rest_request(conninfo, credentials, method, uri,
                                body=body)

@request.request
def get_node_chassis_status(conninfo, credentials, node=None):
    method = "GET"

    if node is not None:
        uri = "/v1/cluster/nodes/{}/chassis".format(node)
    else:
        uri = "/v1/cluster/nodes/chassis/"

    return request.rest_request(conninfo, credentials, method, uri)

# This should match the max_drive_failures enumeration in /v1/cluster/create
PROTECTION_LEVEL_MAP = {
    'RECOMMENDED': -1,
    'TWO_DRIVES': 2,
    'THREE_DRIVES': 3
}

@request.request
def create_cluster(
        conninfo,
        credentials,
        cluster_name,
        admin_password,
        node_uuids=None,
        node_ips=None,
        max_drive_failures='RECOMMENDED',
        eula_accepted=True,
        host_instance_id=None):
    method = "POST"
    uri = "/v1/cluster/create"

    cluster_create_request = {
        'eula_accepted': eula_accepted,
        'cluster_name': str(cluster_name),
        'node_uuids': list() if node_uuids is None else list(node_uuids),
        'node_ips': list() if node_ips is None else list(node_ips),
        'admin_password': str(admin_password),
        'max_drive_failures': max_drive_failures
    }

    if host_instance_id is not None:
        cluster_create_request['host_instance_id'] = host_instance_id

    return request.rest_request(
        conninfo, credentials, method, uri, body=cluster_create_request)

@request.request
def add_node(conninfo, credentials, node_uuids=None, node_ips=None):
    method = "POST"
    uri = "/v1/cluster/nodes/"

    req = {
        'node_uuids': list() if node_uuids is None else list(node_uuids),
        'node_ips': list() if node_ips is None else list(node_ips)
    }

    return request.rest_request(conninfo, credentials, method, uri, body=req)
