# Copyright (c) 2019 Qumulo, Inc.
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
def get_config(conninfo, credentials):
    method = "GET"
    uri = "/v1/audit/config"
    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def set_config(conninfo, credentials,
        enabled=None, server_address=None, server_port=None):
    method = "PATCH"
    uri = "/v1/audit/config"
    body = dict()
    if enabled is not None:
        body['enabled'] = enabled
    if server_address is not None:
        body['server_address'] = server_address
    if server_port is not None:
        body['server_port'] = server_port
    return request.rest_request(conninfo, credentials, method, uri, body=body)

@request.request
def get_status(conninfo, credentials):
    method = "GET"
    uri = "/v1/audit/status"
    return request.rest_request(conninfo, credentials, method, uri)
