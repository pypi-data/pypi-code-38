# Copyright (c) 2017 Qumulo, Inc.
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

# Deprecated, use v2 instead.
@request.request
def settings_set(
        conninfo,
        credentials,
        bind_uri,
        base_dn,
        ldap_schema='RFC2307',
        user='',
        password='',
        gids_extension=False,
        encrypt_connection = True,
        ldap_schema_description=None):

    method = 'PUT'
    uri = '/v1/ldap/settings'

    settings = {
        'bind_uri':           util.check_ascii(bind_uri, 'bind_uri'),
        'base_dn':            util.check_unicode(base_dn, 'base_dn'),
        'ldap_schema':        util.check_ascii(ldap_schema, 'ldap_schema'),
        'user':               util.check_unicode(user, 'user'),
        'gids_extension':     gids_extension,
        'encrypt_connection': encrypt_connection,
    }
    if password is not None:
        settings['password'] = util.check_unicode(password, 'password')
    if ldap_schema_description is not None:
        settings['ldap_schema_description'] = ldap_schema_description

    return request.rest_request(
        conninfo, credentials, method, uri, body=settings)

# Deprecated, use v2 instead.
@request.request
def settings_get(conninfo, credentials):
    method = 'GET'
    uri = '/v1/ldap/settings'

    return request.rest_request(conninfo, credentials, method, uri)

# Deprecated, use v2 instead.
@request.request
def settings_update(
        conninfo,
        credentials,
        bind_uri=None,
        base_dn=None,
        ldap_schema=None,
        user=None,
        password=None,
        gids_extension=None,
        encrypt_connection=None,
        ldap_schema_description=None):
    method = 'PATCH'
    uri = '/v1/ldap/settings'

    settings = {}

    if bind_uri != None:
        settings['bind_uri'] = bind_uri
    if base_dn != None:
        settings['base_dn'] = base_dn
    if ldap_schema != None:
        settings['ldap_schema'] = ldap_schema
    if ldap_schema_description != None:
        settings['ldap_schema_description'] = ldap_schema_description
    if user != None:
        settings['user'] = user
    if password != None:
        settings['password'] = password
    if gids_extension != None:
        settings['gids_extension'] = gids_extension
    if encrypt_connection != None:
        settings['encrypt_connection'] = encrypt_connection

    return request.rest_request(
        conninfo, credentials, method, uri, body=settings)

@request.request
def settings_set_v2(
        conninfo,
        credentials,
        bind_uri,
        base_distinguished_names,
        use_ldap=False,
        user='',
        password='',
        encrypt_connection=True,
        ldap_schema='RFC2307',
        ldap_schema_description=None):

    method = 'PUT'
    uri = '/v2/ldap/settings'

    settings = {
        'use_ldap': use_ldap,
        'bind_uri': util.check_ascii(bind_uri, 'bind_uri'),
        'base_distinguished_names':
            util.check_unicode(
                base_distinguished_names, 'base_distinguished_names'),
        'ldap_schema': util.check_ascii(ldap_schema, 'ldap_schema'),
        'user': util.check_unicode(user, 'user'),
        'encrypt_connection': encrypt_connection,
    }
    if password is not None:
        settings['password'] = util.check_unicode(password, 'password')
    if ldap_schema_description is not None:
        settings['ldap_schema_description'] = ldap_schema_description

    return request.rest_request(
        conninfo, credentials, method, uri, body=settings)

@request.request
def settings_get_v2(conninfo, credentials):
    method = 'GET'
    uri = '/v2/ldap/settings'

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def settings_update_v2(
        conninfo,
        credentials,
        bind_uri=None,
        base_distinguished_names=None,
        use_ldap=None,
        user=None,
        password=None,
        encrypt_connection=None,
        ldap_schema=None,
        ldap_schema_description=None):
    method = 'PATCH'
    uri = '/v2/ldap/settings'

    settings = {}

    if bind_uri != None:
        settings['bind_uri'] = bind_uri
    if base_distinguished_names != None:
        settings['base_distinguished_names'] = base_distinguished_names
    if ldap_schema != None:
        settings['ldap_schema'] = ldap_schema
    if ldap_schema_description != None:
        settings['ldap_schema_description'] = ldap_schema_description
    if user != None:
        settings['user'] = user
    if password != None:
        settings['password'] = password
    if use_ldap != None:
        settings['use_ldap'] = use_ldap
    if encrypt_connection != None:
        settings['encrypt_connection'] = encrypt_connection

    return request.rest_request(
        conninfo, credentials, method, uri, body=settings)

@request.request
def status_get(conninfo, credentials):
    method = 'GET'
    uri = '/v1/ldap/status'

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def uid_number_to_login_name_get(conninfo, credentials, uid_number):
    method = "GET"
    uri = "/v1/ldap/uid-number/" + str(uid_number) + "/login-name"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def login_name_to_gid_numbers_get(conninfo, credentials, login_name):
    method = 'GET'
    uri = '/v1/ldap/login-name/' + str(login_name) + '/gid-numbers'

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def login_name_to_uid_numbers_get(conninfo, credentials, uid):
    method = "GET"
    uri = "/v1/ldap/login-name/" + str(uid) + "/uid-numbers"

    return request.rest_request(conninfo, credentials, method, uri)
