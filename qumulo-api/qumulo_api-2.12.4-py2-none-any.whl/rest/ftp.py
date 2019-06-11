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

@request.request
def get_status(conninfo, credentials):
    return request.rest_request(conninfo, credentials, "GET", "/v0/ftp/status")

@request.request
def get_settings(conninfo, credentials):
    return request.rest_request(
        conninfo, credentials, "GET", "/v0/ftp/settings")

@request.request
def modify_settings(
    conninfo,
    credentials,
    enabled=None,
    check_remote_host=None,
    log_operations=None,
    chroot_users=None,
    allow_unencrypted_connections=None,
    expand_wildcards=None,
    anonymous_user=None,
    greeting=None):
    '''
    Modify FTP settings on the server.
    @a enabled                       -- Turns the FTP server on or off (bool.)
    @a check_remote_host             -- When enabled, disallow data channel
                                        connections remote IPs other than the IP
                                        of the command channel connection
                                        (bool.)
    @a log_operations                -- When enabled, log ftp operations in
                                        /var/log/qumulo/qumulo-ftp.log (bool.)
    @a chroot_users                  -- When enabled, users are restricted to
                                        their home directories if they have one
                                        set (bool.)
    @a allow_unencrypted_connections -- When enabled, allow non-encrypted (FTP
                                        not FTPS) connections to the server
                                        (bool.)
    @a expand_wildcards              -- When enabled, support certain wildcard
                                        characters in FTP commands that would
                                        accept glob patterns on linux-like
                                        FTP servers (i.e. NLST, LIST etc.)
                                        (bool.)
    @ anonymous_user                 -- When set, the server accepts an
                                        anonymous login as the set user. When
                                        given the string 'none' the
                                        anonymous_user is cleared.
                                        (rest.fs.FSIdentity or 'none'.)
    @ greeting                       -- When set, the string to display upon
                                        successful connection.
    '''

    request_body = {}
    if enabled is not None:
        request_body['enabled'] = enabled
    if check_remote_host is not None:
        request_body['check_remote_host'] = check_remote_host
    if log_operations is not None:
        request_body['log_operations'] = log_operations
    if chroot_users is not None:
        request_body['chroot_users'] = chroot_users
    if allow_unencrypted_connections is not None:
        request_body['allow_unencrypted_connections'] = \
            allow_unencrypted_connections
    if expand_wildcards is not None:
        request_body['expand_wildcards'] = expand_wildcards
    if greeting is not None:
        request_body['greeting'] = greeting
    if anonymous_user is not None:
        if isinstance(anonymous_user, str) and anonymous_user == 'none':
            request_body['anonymous_user'] = None
        else:
            request_body['anonymous_user'] = anonymous_user.body()

    return request.rest_request(
        conninfo, credentials, "PATCH", "/v0/ftp/settings", body=request_body)
