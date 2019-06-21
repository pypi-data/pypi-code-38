# Copyright (c) 2015 Qumulo, Inc.
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
def resolve(conninfo, credentials, ips):
    '''
    DEPRECATED: Use resolve_ips_to_names() instead.
    '''

    method = "POST"
    uri = "/v1/dns/resolve-ips-to-names"
    return request.rest_request(conninfo, credentials, method, uri, body=ips)

@request.request
def resolve_ips_to_names(conninfo, credentials, ips):
    method = "POST"
    uri = "/v1/dns/resolve-ips-to-names"
    return request.rest_request(conninfo, credentials, method, uri, body=ips)

@request.request
def resolve_names_to_ips(conninfo, credentials, ips):
    method = "POST"
    uri = "/v1/dns/resolve-names-to-ips"
    return request.rest_request(conninfo, credentials, method, uri, body=ips)

@request.request
def lookup_overrides_get(conninfo, credentials):
    method = "GET"
    uri = "/v1/dns/lookup-override-config"
    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def lookup_overrides_set(conninfo, credentials, overrides):
    method = "PUT"
    uri = "/v1/dns/lookup-override-config"
    return request.rest_request(
        conninfo, credentials, method, uri, body=overrides)
