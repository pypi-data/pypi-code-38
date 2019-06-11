# Copyright (c) 2013 Qumulo, Inc.
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
import qumulo.lib.util as util

@request.request
def list_ad(conninfo, credentials):
    method = "GET"
    uri = "/v1/ad/status"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def poll_ad(conninfo, credentials):
    method = "GET"
    uri = "/v1/ad/monitor"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def join_ad(
        conninfo, credentials, domain, username, password,
        ou=None, domain_netbios=None, enable_ldap=False, base_dn=None):
    method = "POST"
    uri = "/v1/ad/join"

    if ou is None:
        ou = ""
    if domain_netbios is None:
        domain_netbios = ""
    if base_dn is None:
        base_dn = ""

    config = {
        "domain":         util.check_ascii(domain, 'domain'),
        "domain_netbios": util.check_ascii(domain_netbios, 'domain_netbios'),
        "user":           util.check_ascii(username, 'username'),
        "password":       util.check_ascii(password, 'password'),
        "ou":             util.check_ascii(ou, 'ou'),
        "use_ad_posix_attributes": enable_ldap,
        "base_dn":        util.check_ascii(base_dn, 'base_dn'),
    }

    return request.rest_request(conninfo, credentials, method, uri, body=config)

@request.request
def leave_ad(conninfo, credentials, domain, username, password):
    method = "POST"
    uri = "/v1/ad/leave"

    # XXX scott: support none for these in the api, also, don't call domain
    # assistant script in that case
    if username is None:
        username = ""
    if password is None:
        password = ""

    config = {
        "domain":   util.check_ascii(domain, 'domain'),
        "user":     util.check_ascii(username, 'username'),
        "password": util.check_ascii(password, 'password')
    }

    return request.rest_request(conninfo, credentials, method, uri, body=config)

@request.request
def cancel_ad(conninfo, credentials):
    method = "POST"
    uri = "/v1/ad/cancel"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def uid_to_sid_get(conninfo, credentials, uid):
    method = "GET"
    uri = "/v1/ad/uids/" + str(uid) + "/sids/"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def username_to_sid_get(conninfo, credentials, name):
    return request.rest_request(conninfo, credentials, "GET",
        "/v1/ad/usernames/{}/sids/".format(name))

@request.request
def sid_to_uid_get(conninfo, credentials, sid):
    method = "GET"
    uri = "/v1/ad/sids/" + sid + "/uid"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def sid_to_username_get(conninfo, credentials, sid):
    return request.rest_request(conninfo, credentials, "GET",
        "/v1/ad/sids/{}/username".format(sid))

@request.request
def sid_to_gid_get(conninfo, credentials, sid):
    method = "GET"
    uri = "/v1/ad/sids/" + sid + "/gid"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def gid_to_sid_get(conninfo, credentials, gid):
    method = "GET"
    uri = "/v1/ad/gids/" + str(gid) + "/sids/"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def sid_to_expanded_group_sids_get(conninfo, credentials, sid):
    method = "GET"
    uri = "/v1/ad/sids/" + sid + "/expanded-groups/"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def clear_cache_post(conninfo, credentials):
    method = "POST"
    uri = '/v1/ad/clear-cache'

    return request.rest_request(conninfo, credentials, method, uri)
