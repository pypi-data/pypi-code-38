# Copyright (c) 2018 Qumulo, Inc.
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

#  _              _        _
# | | _____ _   _| |_ __ _| |__
# | |/ / _ \ | | | __/ _` | '_ \
# |   <  __/ |_| | || (_| | |_) |
# |_|\_\___|\__, |\__\__,_|_.__/
#           |___/
#  FIGLET: keytab
#

@request.request
def set_keytab_file(conninfo, credentials, keytab_file):
    method = "PUT"
    uri = '/v1/auth/kerberos-keytab'

    return request.rest_request(
        conninfo,
        credentials,
        method,
        uri,
        body_file=keytab_file,
        request_content_type=request.CONTENT_TYPE_BINARY)

@request.request
def set_keytab(conninfo, credentials, keytab_contents):
    method = "PUT"
    uri = '/v1/auth/kerberos-keytab'

    return request.rest_request(
        conninfo, credentials, method, uri, body=keytab_contents)

@request.request
def delete_keytab(conninfo, credentials):
    method = "DELETE"
    uri = '/v1/auth/kerberos-keytab'

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def get_keytab(conninfo, credentials):
    method = "GET"
    uri = '/v1/auth/kerberos-keytab'

    return request.rest_request(conninfo, credentials, method, uri)

#           _   _   _
#  ___  ___| |_| |_(_)_ __   __ _ ___
# / __|/ _ \ __| __| | '_ \ / _` / __|
# \__ \  __/ |_| |_| | | | | (_| \__ \
# |___/\___|\__|\__|_|_| |_|\__, |___/
#                           |___/
#  FIGLET: settings
#

@request.request
def modify_settings(conninfo, credentials, use_alt_security_identities_mapping):
    method = "PUT"
    uri = '/v1/auth/kerberos-settings'

    body = {
        "use_alt_security_identities_mapping":
            use_alt_security_identities_mapping,
    }

    return request.rest_request(
        conninfo, credentials, method, uri, body=body)

@request.request
def get_settings(conninfo, credentials):
    method = "GET"
    uri = '/v1/auth/kerberos-settings'

    return request.rest_request(conninfo, credentials, method, uri)
