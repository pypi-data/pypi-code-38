# Copyright (c) 2016 Qumulo, Inc.
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
from qumulo.lib.uri import UriBuilder

@request.request
def replicate(conninfo, credentials, relationship):
    method = "POST"
    uri = "/v1/replication/source-relationships/{}/replicate".format(
        relationship)
    return request.rest_request(
        conninfo, credentials, method, unicode(uri))

@request.request
def create_source_relationship(
        conninfo,
        credentials,
        target_path,
        address,
        source_id=None,
        source_path=None,
        source_root_read_only=None,
        continuous_replication_enabled=None,
        target_port=None):

    body = {
        'target_root_path': target_path,
        'target_address': address
    }

    if source_id is not None:
        body['source_root_id'] = source_id

    if source_path is not None:
        body['source_root_path'] = source_path

    if source_root_read_only is not None:
        body['source_root_read_only'] = source_root_read_only

    if target_port is not None:
        body['target_port'] = target_port

    if continuous_replication_enabled is not None:
        body['continuous_replication_enabled'] = continuous_replication_enabled

    method = "POST"
    uri = "/v1/replication/source-relationships/"
    return request.rest_request(conninfo, credentials, method, uri, body=body)

@request.request
def list_source_relationships(conninfo, credentials):
    method = "GET"
    uri = "/v1/replication/source-relationships/"
    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def get_source_relationship(conninfo, credentials, relationship_id):
    method = "GET"
    uri = "/v1/replication/source-relationships/{}"
    return request.rest_request(
        conninfo, credentials, method, uri.format(relationship_id))

@request.request
def delete_source_relationship(conninfo, credentials, relationship_id):
    method = "DELETE"
    uri = "/v1/replication/source-relationships/{}"
    return request.rest_request(
        conninfo, credentials, method, uri.format(relationship_id))

@request.request
def delete_target_relationship(conninfo, credentials, relationship_id):
    method = "POST"
    uri = "/v1/replication/target-relationships/{}/delete"
    return request.rest_request(
        conninfo, credentials, method, uri.format(relationship_id))

@request.request
def modify_source_relationship(
        conninfo, credentials,
        relationship_id,
        new_target_address=None,
        new_target_port=None,
        source_root_read_only=None,
        continuous_replication_enabled=None,
        blackout_windows=None,
        blackout_window_timezone=None,
        etag=None):

    method = "PATCH"
    uri = "/v1/replication/source-relationships/{}"

    body = {}
    if new_target_address is not None:
        body['target_address'] = new_target_address
    if new_target_port is not None:
        body['target_port'] = new_target_port
    if source_root_read_only is not None:
        body['source_root_read_only'] = source_root_read_only
    if continuous_replication_enabled is not None:
        body['continuous_replication_enabled'] = continuous_replication_enabled
    if blackout_windows is not None:
        body['blackout_windows'] = blackout_windows
    if blackout_window_timezone is not None:
        body['blackout_window_timezone'] = blackout_window_timezone

    return request.rest_request(
        conninfo, credentials, method, uri.format(relationship_id), body=body,
        if_match=etag)

@request.request
def list_source_relationship_statuses(conninfo, credentials):
    method = "GET"
    uri = "/v1/replication/source-relationships/status/"
    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def list_target_relationship_statuses(conninfo, credentials):
    method = "GET"
    uri = "/v1/replication/target-relationships/status/"
    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def get_source_relationship_status(conninfo, credentials, relationship_id):
    method = "GET"
    uri = "/v1/replication/source-relationships/{}/status"
    return request.rest_request(
        conninfo, credentials, method, uri.format(relationship_id))

@request.request
def get_target_relationship_status(conninfo, credentials, relationship_id):
    method = "GET"
    uri = "/v1/replication/target-relationships/{}/status"
    return request.rest_request(
        conninfo, credentials, method, uri.format(relationship_id))

@request.request
def authorize(
        conninfo,
        credentials,
        relationship_id,
        allow_non_empty_directory=None,
        allow_fs_path_create=None):
    method = "POST"

    uri = UriBuilder(
        path="/v1/replication/target-relationships/{}/authorize".format(
            relationship_id))

    if allow_non_empty_directory is not None:
        uri.add_query_param(
            "allow-non-empty-directory",
            "true" if allow_non_empty_directory else "false")
    if allow_fs_path_create is not None:
        uri.add_query_param(
            "allow-fs-path-create",
            "true" if allow_fs_path_create else "false")

    return request.rest_request(
        conninfo, credentials, method, unicode(uri))

@request.request
def reconnect_target_relationship(conninfo, credentials, relationship_id):
    method = "POST"
    uri = "/v1/replication/target-relationships/{}/reconnect"
    return request.rest_request(
        conninfo, credentials, method, uri.format(relationship_id))

@request.request
def abort_replication(conninfo, credentials, relationship_id):
    method = "POST"
    uri = "/v1/replication/source-relationships/{}/abort-replication"
    return request.rest_request(
        conninfo, credentials, method, uri.format(relationship_id))

@request.request
def make_target_writable(conninfo, credentials, relationship_id):
    method = "POST"
    uri = "/v1/replication/target-relationships/{}/make-writable"
    return request.rest_request(
        conninfo, credentials, method, uri.format(relationship_id))

@request.request
def reverse_target_relationship(
        conninfo, credentials,
        relationship_id,
        source_address,
        source_port=None):
    method = "POST"
    uri = "/v1/replication/source-relationships/reverse-target-relationship"

    body = {
        'target_relationship_id': relationship_id,
        'source_address': source_address
    }
    if source_port is not None:
        body['source_port'] = source_port

    return request.rest_request(conninfo, credentials, method, uri, body=body)
