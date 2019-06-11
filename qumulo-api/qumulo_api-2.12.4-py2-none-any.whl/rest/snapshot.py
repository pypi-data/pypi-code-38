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
import qumulo.rest.fs
from qumulo.lib.uri import UriBuilder

@request.request
def create_snapshot(
        conninfo, credentials, name=None, expiration=None, time_to_live=None,
        path=None, id_=None):
    method = 'POST'
    uri = '/v2/snapshots/'
    snapshot = {}

    # name is an optional parameter
    if name != None:
        snapshot['name'] = name
    # expiration is an optional parameter
    if expiration != None:
        snapshot['expiration'] = expiration
    # time_to_live is an optional parameter
    if time_to_live != None:
        uri += '?expiration-time-to-live=' + time_to_live

    # Take a snapshot on a particular path or ID
    if path != None:
        id_ = qumulo.rest.fs.get_attr(
            conninfo, credentials, path).lookup('file_number')
    if id_ != None:
        snapshot['source_file_id'] = id_

    return request.rest_request(conninfo, credentials, method, uri,
        body=snapshot)

@request.request
def modify_snapshot(
        conninfo, credentials, snapshot_id, expiration=None, time_to_live=None):
    method = 'PATCH'
    uri = '/v2/snapshots/{}'
    snapshot = {}

    # expiration is an optional parameter
    if expiration != None:
        snapshot['expiration'] = expiration
    # time_to_live is an optional parameter
    if time_to_live != None:
        uri += '?expiration-time-to-live=' + time_to_live

    return request.rest_request(conninfo, credentials, method,
        uri.format(snapshot_id), body=snapshot)

@request.request
def list_snapshots(conninfo, credentials, include_in_delete=False):
    method = 'GET'
    include_in_delete_ = "true" if include_in_delete else "false"
    uri = '/v2/snapshots/?include-in-delete=%s' % include_in_delete_

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def get_snapshot(conninfo, credentials, snapshot_id):
    method = 'GET'
    uri = '/v2/snapshots/{}'

    return request.rest_request(conninfo, credentials, method,
        uri.format(snapshot_id))

@request.request
def list_snapshot_statuses(conninfo, credentials):
    method = 'GET'
    uri = '/v2/snapshots/status/'

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def get_snapshot_status(conninfo, credentials, snapshot_id):
    method = 'GET'
    uri = '/v2/snapshots/status/{}'

    return request.rest_request(conninfo, credentials, method,
        uri.format(snapshot_id))

@request.request
def delete_snapshot(conninfo, credentials, snapshot_id):
    method = 'DELETE'
    uri = '/v2/snapshots/{}'

    return request.rest_request(conninfo, credentials, method,
        uri.format(snapshot_id))

@request.request
def create_policy(conninfo, credentials, name, schedule_info,
                  directory_id=None, enabled=None):

    method = 'POST'
    uri = '/v1/snapshots/policies/'

    if directory_id == None:
        directory_id = "2"

    policy = {
        'name': name,
        'schedules': [schedule_info],
        'source_file_ids': [directory_id]
    }

    if enabled is not None:
        policy['enabled'] = enabled

    return request.rest_request(conninfo, credentials, method, uri, body=policy)

@request.request
def modify_policy(conninfo, credentials, policy_id,
                  name=None, source_file_id=None,
                  schedule_info=None, enabled=None, if_match=None):

    method = 'PATCH'
    uri = '/v1/snapshots/policies/{}'

    policy = {}
    if name is not None:
        policy.update({'name' : name})
    if source_file_id is not None:
        policy.update({'source_file_ids' : [str(source_file_id)]})
    if schedule_info is not None:
        policy.update({'schedules' : [schedule_info]})
    if enabled is not None:
        policy['enabled'] = enabled

    return request.rest_request(
        conninfo, credentials, method, uri.format(policy_id), body=policy,
        if_match=if_match)

@request.request
def list_policies(conninfo, credentials):
    method = 'GET'
    uri = '/v1/snapshots/policies/'

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def get_policy(conninfo, credentials, policy_id):
    method = 'GET'
    uri = '/v1/snapshots/policies/{}'

    return request.rest_request(
        conninfo, credentials, method, uri.format(policy_id))

@request.request
def delete_policy(conninfo, credentials, policy_id):
    method = 'DELETE'
    uri = '/v1/snapshots/policies/{}'

    return request.rest_request(
        conninfo, credentials, method, uri.format(policy_id))

@request.request
def list_policy_statuses(conninfo, credentials):
    method = 'GET'
    uri = '/v1/snapshots/policies/status/'

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def get_policy_status(conninfo, credentials, policy_id):
    method = 'GET'
    uri = '/v1/snapshots/policies/status/{}'

    return request.rest_request(
        conninfo, credentials, method, uri.format(policy_id))

@request.request
def get_total_used_capacity(conninfo, credentials):
    method = 'GET'
    uri = '/v1/snapshots/total-used-capacity'

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def calculate_used_capacity(conninfo, credentials, ids):
    method = 'POST'
    uri = '/v1/snapshots/calculate-used-capacity'

    return request.rest_request(conninfo, credentials, method, uri, body=ids)

@request.request
def capacity_used_per_snapshot(conninfo, credentials):
    method = 'GET'
    uri = '/v1/snapshots/capacity-used-per-snapshot/'

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def capacity_used_by_snapshot(conninfo, credentials, snapshot_id):
    method = 'GET'
    uri = '/v1/snapshots/capacity-used-per-snapshot/{}'

    return request.rest_request(
        conninfo, credentials, method, uri.format(snapshot_id))

@request.request
def get_snapshot_tree_diff(
        conninfo, credentials, newer_snap, older_snap, limit=None, after=None):
    method = 'GET'
    uri = UriBuilder(path='/v2/snapshots/{:d}/changes-since/{:d}'.format(
            newer_snap, older_snap))

    if limit is not None:
        uri.add_query_param('limit', limit)

    if after is not None:
        uri.add_query_param('after', after)

    return request.rest_request(conninfo, credentials, method, unicode(uri))

@request.request
def get_all_snapshot_tree_diff(
        conninfo, credentials, newer_snap, older_snap, limit=None):
    uri = UriBuilder(path='/v2/snapshots/{:d}/changes-since/{:d}'.format(
            newer_snap, older_snap))

    def get_a_snapshot_tree_diff(uri):
        return request.rest_request(conninfo, credentials, 'GET', unicode(uri))

    return request.PagingIterator(
        unicode(uri), get_a_snapshot_tree_diff, page_size=limit)

def get_snapshot_file_diff_uri(newer_snap, older_snap, path, file_id):
    assert (path is not None) ^ (file_id is not None)
    file_ref = unicode(path if path else file_id)

    return UriBuilder(
        path='/v2/snapshots/{:d}/changes-since/{:d}/files'.format(
            newer_snap, older_snap)).add_path_component(file_ref)

@request.request
def get_snapshot_file_diff(
        conninfo, credentials, newer_snap, older_snap,
        path=None, file_id=None, limit=None, after=None):
    uri = get_snapshot_file_diff_uri(newer_snap, older_snap, path, file_id)
    if limit is not None:
        uri.add_query_param('limit', limit)
    if after is not None:
        uri.add_query_param('after', after)

    return request.rest_request(conninfo, credentials, 'GET', unicode(uri))

@request.request
def get_all_snapshot_file_diff(
        conninfo, credentials, newer_snap, older_snap,
        path=None, file_id=None, limit=None):
    uri = get_snapshot_file_diff_uri(newer_snap, older_snap, path, file_id)

    def get_a_snapshot_file_diff(uri):
        return request.rest_request(conninfo, credentials, 'GET', unicode(uri))

    return request.PagingIterator(
        unicode(uri), get_a_snapshot_file_diff, page_size=limit)
