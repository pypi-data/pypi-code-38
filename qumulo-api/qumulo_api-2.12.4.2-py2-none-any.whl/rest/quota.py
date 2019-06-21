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
def get_all_quotas(conninfo, credentials, page_size=None, if_match=None):
    def get_a_quota(uri):
        return request.rest_request(
            conninfo, credentials, "GET", unicode(uri), if_match=if_match)

    return request.PagingIterator(
        '/v1/files/quotas/', get_a_quota, page_size=page_size)

@request.request
def get_all_quotas_with_status(
        conninfo, credentials, page_size=None, if_match=None):
    def get_a_quota(uri):
        return request.rest_request(
            conninfo, credentials, "GET", unicode(uri), if_match=if_match)

    return request.PagingIterator(
        '/v1/files/quotas/status/', get_a_quota, page_size=page_size)

@request.request
def get_quota_with_status(conninfo, credentials, id_, if_match=None):
    method = "GET"
    uri = UriBuilder(path="/v1/files/quotas/status/{}".format(id_))
    return request.rest_request(
        conninfo, credentials, method, unicode(uri), if_match=if_match)

@request.request
def get_quota(conninfo, credentials, id_, if_match=None):
    method = "GET"
    uri = UriBuilder(path="/v1/files/quotas/{}".format(id_))
    return request.rest_request(
        conninfo, credentials, method, unicode(uri), if_match=if_match)

@request.request
def create_quota(conninfo, credentials, id_, limit_in_bytes):
    body = {'id': str(id_), 'limit': str(limit_in_bytes)}
    method = "POST"
    uri = UriBuilder(path="/v1/files/quotas/", rstrip_slash=False)
    return request.rest_request(
        conninfo, credentials, method, unicode(uri), body=body)

@request.request
def update_quota(conninfo, credentials, id_, limit_in_bytes, if_match=None):
    body = {'id': str(id_), 'limit': str(limit_in_bytes)}
    method = "PUT"
    uri = UriBuilder(path="/v1/files/quotas/{}".format(id_))
    return request.rest_request(
        conninfo,
        credentials,
        method,
        unicode(uri),
        body=body,
        if_match=if_match)

@request.request
def delete_quota(conninfo, credentials, id_, if_match=None):
    method = "DELETE"
    uri = UriBuilder(path="/v1/files/quotas/{}".format(id_))
    return request.rest_request(
        conninfo, credentials, method, unicode(uri), if_match=if_match)
