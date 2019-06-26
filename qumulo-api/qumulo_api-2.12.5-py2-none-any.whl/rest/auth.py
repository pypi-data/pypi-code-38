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

import time

import qumulo.lib.request as request
from qumulo.lib.uri import UriBuilder
import qumulo.lib.util as util

@request.request
def login(conninfo, credentials, username, password):
    method = "POST"
    uri = "/v1/session/login"

    login_info = {
        'username': util.check_unicode(username, 'username'),
        'password': util.check_unicode(password, 'password'),
    }
    resp = request.rest_request(conninfo, credentials, method, uri,
                                body=login_info)
    # Authorization uses deltas in time, so we store this systems unix epoch as
    # the issue date.  That way time deltas can be computed locally.
    # Server uses its own time deltas so the clocks must tick at the same rate.
    resp[0]['issue'] = int(time.time())
    return resp

@request.request
def change_password(conninfo, credentials, old_password, new_password):
    "Unlike SetUserPassword, acts implicitly on logged in user"

    method = "POST"
    uri = "/v1/session/change-password"
    body = {
        'old_password': util.check_unicode(old_password, 'old password'),
        'new_password': util.check_unicode(new_password, 'new password')
    }

    return request.rest_request(conninfo, credentials, method, uri, body=body)

@request.request
def who_am_i(conninfo, credentials):
    "Same as GET on user/<current_id>"

    return request.rest_request(
        conninfo, credentials, "GET", "/v1/session/who-am-i")

@request.request
def auth_id_to_all_related_identities(conninfo, credentials, auth_id):
    method = "GET"
    uri = "/v1/auth/auth-ids/{}/related-identities/".format(auth_id)

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def posix_uid_to_all_related_identities(conninfo, credentials, posix_uid):
    method = "GET"
    uri = "/v1/auth/posix-uids/{}/related-identities/".format(posix_uid)

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def posix_gid_to_all_related_identities(conninfo, credentials, posix_gid):
    method = "GET"
    uri = "/v1/auth/posix-gids/{}/related-identities/".format(posix_gid)

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def sid_to_all_related_identities(conninfo, credentials, sid):
    method = "GET"
    uri = "/v1/auth/sids/{}/related-identities/".format(sid)

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def local_username_to_all_related_identities(conninfo, credentials, username):
    method = "GET"
    uri = UriBuilder(path="/v1/auth/local-username")
    uri.add_path_component(util.check_unicode(username, 'username'))
    uri.add_path_component('related-identities')
    uri.append_slash()
    return request.rest_request(conninfo, credentials, method, str(uri))

@request.request
def user_defined_mappings_set(conninfo, credentials, mappings):
    method = "PUT"
    uri = "/v1/auth/user-defined-mappings/"

    return request.rest_request(
        conninfo, credentials, method, uri, body=mappings)

@request.request
def user_defined_mappings_get(conninfo, credentials):
    method = "GET"
    uri = "/v1/auth/user-defined-mappings/"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def clear_cache(conninfo, credentials):
    request.rest_request(conninfo, credentials, "POST", "/v1/auth/clear-cache")

@request.request
def find_identity(conninfo, credentials, **attrs):
    '''
    Obtain a fully-populated api_identity object. At least one argument other
    than @p domain must be specified. If multiple are specified, they must
    represent the same identity.
    @p domain The domain the identity is in.  LOCAL_DOMAIN, WORLD_DOMAIN,
        POSIX_USER_DOMAIN, POSIX_GROUP_DOMAIN, or AD_DOMAIN.
    @p auth_id The identifier used internally by qsfs.
    @p uid A posix UID
    @p gid A posix GID
    @p sid A SID.
    @p name A name of a cluster-local, AD, or LDAP user.  May be an unqualified
        login name, qualified with netbios name (e.g. DOMAIN\user), a
        universal principal name (e.g. user@domain.example.com), or an LDAP
        distinguished name (e.g CN=John Doe,OU=users,DC=example,DC=com).
    '''
    return request.rest_request(
        conninfo, credentials, "POST", "/v1/auth/identity/find", body=attrs)
