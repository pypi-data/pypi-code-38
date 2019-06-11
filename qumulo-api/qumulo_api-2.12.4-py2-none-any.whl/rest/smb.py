# Copyright (c) 2012 Qumulo, Inc.
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
import qumulo.lib.obj as obj
from qumulo.lib.uri import UriBuilder

@request.request
def smb_list_shares_v1(conninfo, credentials):
    '''
    Deprecated.  List all shares, with read_only/allow_guest_access permissions
    flags displayed (even if permissions are more complex)
    '''
    method = "GET"
    uri = "/v1/smb/shares/"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def smb_list_share_v1(conninfo, credentials, id_):
    '''
    Deprecated.  Get a given share, with read_only/allow_guest_access
    permissions flags displayed (even if permissions are more complex)
    '''
    id_ = unicode(id_)

    method = "GET"
    uri = "/v1/smb/shares/%s" % id_

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def smb_list_shares(conninfo, credentials):
    return request.rest_request(conninfo, credentials, "GET", "/v2/smb/shares/")

@request.request
def smb_list_share(conninfo, credentials, id_=None, name=None):
    assert [id_, name].count(None) == 1

    method = "GET"
    uri = str(
        UriBuilder(path="/v2/smb/shares").add_path_component(id_ or name))

    return request.rest_request(conninfo, credentials, method, uri)

# Permissions constants
NO_ACCESS = u'NONE'
READ_ACCESS = u'READ'
WRITE_ACCESS = u'WRITE'
CHANGE_PERMISSIONS_ACCESS = u'CHANGE_PERMISSIONS'
ALL_ACCESS = u'ALL'

ALLOWED_TYPE = u'ALLOWED'
DENIED_TYPE = u'DENIED'

@request.request
def smb_add_share(conninfo, credentials,
        share_name,
        fs_path,
        description,
        read_only=None,
        allow_guest_access=None,
        allow_fs_path_create=False,
        access_based_enumeration_enabled=False,
        default_file_create_mode=None,
        default_directory_create_mode=None,
        permissions=None,
        bytes_per_sector=None):
    allow_fs_path_create_ = "true" if allow_fs_path_create else "false"

    if permissions is None:
        if bytes_per_sector is not None:
            raise ValueError(
                'bytes_per_sector requires permissions be specified')

        # Use the old v1 API and its semantics (i.e. default full control but
        # deny guest)
        share_info = {
            'share_name':         share_name,
            'fs_path':            fs_path,
            'description':        description,
            'read_only':          bool(read_only),
            'allow_guest_access': bool(allow_guest_access),
            'access_based_enumeration_enabled': \
                bool(access_based_enumeration_enabled)
        }

        if default_file_create_mode is not None:
            share_info['default_file_create_mode'] = default_file_create_mode
        if default_directory_create_mode is not None:
            share_info['default_directory_create_mode'] = \
                default_directory_create_mode

        uri = str(UriBuilder(path="/v1/smb/shares/", rstrip_slash=False).
            add_query_param("allow-fs-path-create", allow_fs_path_create_))

        return request.rest_request(conninfo, credentials, "POST", uri,
            body=share_info)
    else:
        # Use the new API.
        if read_only is not None:
            raise ValueError("read_only may not be specified with permissions")
        if allow_guest_access is not None:
            raise ValueError(
                "allow_guest_access may not be specified with permissions")

        share_info = {
            'share_name':  share_name,
            'fs_path':     fs_path,
            'description': description,
            'permissions': permissions,
        }
        if access_based_enumeration_enabled is not None:
            share_info['access_based_enumeration_enabled'] = bool(
                access_based_enumeration_enabled)
        if default_file_create_mode is not None:
            share_info['default_file_create_mode'] = \
                default_file_create_mode
        if default_directory_create_mode is not None:
            share_info['default_directory_create_mode'] = \
                default_directory_create_mode
        if bytes_per_sector is not None:
            share_info['bytes_per_sector'] = str(bytes_per_sector)

        uri = str(UriBuilder(path="/v2/smb/shares/", rstrip_slash=False).
            add_query_param("allow-fs-path-create", allow_fs_path_create_))

        return request.rest_request(conninfo, credentials, "POST", uri,
            body=share_info)

@request.request
def smb_modify_share(conninfo,
        credentials,
        id_=None,
        old_name=None,
        share_name=None,
        fs_path=None,
        description=None,
        permissions=None,
        allow_fs_path_create=False,
        access_based_enumeration_enabled=None,
        default_file_create_mode=None,
        default_directory_create_mode=None,
        bytes_per_sector=None,
        if_match=None):
    assert [id_, old_name].count(None) == 1

    allow_fs_path_create_ = "true" if allow_fs_path_create else "false"
    if_match = None if if_match is None else if_match

    method = "PATCH"
    uri = str(
        UriBuilder(path="/v2/smb/shares/").
        add_path_component(id_ or old_name).
        add_query_param("allow-fs-path-create", allow_fs_path_create_))

    share_info = {}
    if share_name is not None:
        share_info['share_name'] = share_name
    if fs_path is not None:
        share_info['fs_path'] = fs_path
    if description is not None:
        share_info['description'] = description
    if permissions is not None:
        share_info['permissions'] = permissions
    if access_based_enumeration_enabled is not None:
        share_info['access_based_enumeration_enabled'] = \
            bool(access_based_enumeration_enabled)
    if default_file_create_mode is not None:
        share_info['default_file_create_mode'] = \
            default_file_create_mode
    if default_directory_create_mode is not None:
        share_info['default_directory_create_mode'] = \
            default_directory_create_mode
    if bytes_per_sector is not None:
        share_info['bytes_per_sector'] = str(bytes_per_sector)

    return request.rest_request(conninfo, credentials, method, uri,
        body=share_info, if_match=if_match)

@request.request
def smb_set_share(conninfo,
        credentials,
        id_,
        share_name,
        fs_path,
        description,
        permissions,
        allow_fs_path_create=False,
        access_based_enumeration_enabled=None,
        default_file_create_mode=None,
        default_directory_create_mode=None,
        if_match=None):
    '''
    Replaces all share attributes.  The result is a share identical to what
    would have been produced if the same arguments were given on creation.
    Note that this means that an unspecified optional argument will result in
    that attribute being reset to default, even if the share currently has a
    non-default value.
    '''
    allow_fs_path_create_ = "true" if allow_fs_path_create else "false"
    id_ = id_
    share_info = {
        'id': id_,
        'share_name':  share_name,
        'fs_path':     fs_path,
        'description': description,
        'permissions': permissions,
    }
    if access_based_enumeration_enabled is not None:
        share_info['access_based_enumeration_enabled'] = \
            bool(access_based_enumeration_enabled)
    if default_file_create_mode is not None:
        share_info['default_file_create_mode'] = \
            default_file_create_mode
    if default_directory_create_mode is not None:
        share_info['default_directory_create_mode'] = \
            default_directory_create_mode

    uri = str(
        UriBuilder(path="/v2/smb/shares/")
        .add_path_component(id_)
        .add_query_param("allow-fs-path-create", allow_fs_path_create_))

    if_match = None if if_match is None else if_match
    return request.rest_request(conninfo, credentials, "PUT", uri,
        body=share_info, if_match=if_match)

@request.request
def smb_delete_share(conninfo, credentials, id_=None, name=None):
    assert [id_, name].count(None) == 1

    method = "DELETE"
    uri = str(UriBuilder(path="/v2/smb/shares").add_path_component(id_ or name))
    return request.rest_request(conninfo, credentials, method, uri)

class NFSRestriction(obj.Object):
    @classmethod
    def create_default(cls):
        return cls({'read_only': False, 'host_restrictions': [],
                    'user_mapping': 'NFS_MAP_NONE', 'map_to_user_id': '0'})
