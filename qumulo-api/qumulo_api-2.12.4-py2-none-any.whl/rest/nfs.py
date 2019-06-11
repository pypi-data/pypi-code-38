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

class NFSRestriction(obj.Object):
    @classmethod
    def create_default(cls):
        return cls({'read_only': False, 'host_restrictions': [],
                    'user_mapping': 'NFS_MAP_NONE', 'map_to_user_id': '0'})

class NFSExportRestriction(obj.Object):
    @classmethod
    def create_default(cls):
        return cls({'read_only': False, 'host_restrictions': [],
                'user_mapping': 'NFS_MAP_NONE', 'map_to_user': {
                'id_type': 'LOCAL_USER', 'id_value': '0' }})

@request.request
def nfs_list_shares(conninfo, credentials):
    method = "GET"
    uri = "/v1/nfs/shares/"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def nfs_add_share(conninfo, credentials, export_path, fs_path, description,
                  restrictions, allow_fs_path_create=False):
    method = "POST"
    allow_fs_path_create_ = "true" if allow_fs_path_create else "false"
    uri = "/v1/nfs/shares/?allow-fs-path-create=%s" % allow_fs_path_create_

    share_info = {
        'export_path':  export_path,
        'fs_path':      fs_path,
        'description':  description,
        'restrictions': [r.dictionary() for r in restrictions]
    }

    return request.rest_request(conninfo, credentials, method, uri,
        body=share_info)

@request.request
def nfs_list_share(conninfo, credentials, id_):

    method = "GET"
    uri = "/v1/nfs/shares/%s" % id_

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def nfs_modify_share(conninfo, credentials, id_, export_path, fs_path,
                     description, restrictions, allow_fs_path_create=False,
                     if_match=None):

    allow_fs_path_create_ = "true" if allow_fs_path_create else "false"

    if_match = if_match if if_match is None else if_match

    method = "PUT"
    uri = "/v1/nfs/shares/%s?allow-fs-path-create=%s" % \
        (id_, allow_fs_path_create_)

    share_info = {
        'id': id_,
        'export_path':  export_path,
        'fs_path':      fs_path,
        'description':  description,
        'restrictions': [r.dictionary() for r in restrictions]
    }

    return request.rest_request(conninfo, credentials, method, uri,
        body=share_info, if_match=if_match)

@request.request
def nfs_delete_share(conninfo, credentials, id_):

    method = "DELETE"
    uri = "/v1/nfs/shares/%s" % id_

    return request.rest_request(conninfo, credentials, method, uri)

# __     ______    _   _ _____ ____    _____                       _
# \ \   / /___ \  | \ | |  ___/ ___|  | ____|_  ___ __   ___  _ __| |_
#  \ \ / /  __) | |  \| | |_  \___ \  |  _| \ \/ / '_ \ / _ \| '__| __|
#   \ V /  / __/  | |\  |  _|  ___) | | |___ >  <| |_) | (_) | |  | |_
#    \_/  |_____| |_| \_|_|   |____/  |_____/_/\_\ .__/ \___/|_|   \__|
#                                                |_|
# Figlet: V2 NFS Export

@request.request
def nfs_list_exports(conninfo, credentials):
    method = "GET"
    uri = "/v2/nfs/exports/"

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def nfs_add_export(
        conninfo,
        credentials,
        export_path,
        fs_path,
        description,
        restrictions,
        allow_fs_path_create=False,
        present_64_bit_fields_as_32_bit=False):

    method = "POST"
    allow_fs_path_create_ = "true" if allow_fs_path_create else "false"

    uri = str(UriBuilder(path="/v2/nfs/exports/", rstrip_slash=False).
            add_query_param("allow-fs-path-create", allow_fs_path_create_))

    share_info = {
        'export_path':  export_path,
        'fs_path':      fs_path,
        'description':  description,
        'restrictions': [r.dictionary() for r in restrictions],
        'present_64_bit_fields_as_32_bit': present_64_bit_fields_as_32_bit,
    }

    return request.rest_request(conninfo, credentials, method, uri,
        body=share_info)

@request.request
def nfs_get_export(conninfo, credentials, id_=None, export_path=None):
    assert [id_, export_path].count(None) == 1

    method = "GET"
    uri = str(
        UriBuilder(path="/v2/nfs/exports/").
        add_path_component(id_ or export_path))

    return request.rest_request(conninfo, credentials, method, uri)

@request.request
def nfs_modify_export(conninfo,
        credentials,
        id_,
        export_path,
        fs_path,
        description,
        restrictions,
        allow_fs_path_create=False,
        present_64_bit_fields_as_32_bit=False,
        if_match=None):

    allow_fs_path_create_ = "true" if allow_fs_path_create else "false"

    if_match = if_match if if_match is None else if_match

    method = "PUT"
    uri = str(
        UriBuilder(path="/v2/nfs/exports/").
        add_path_component(id_).
        add_query_param("allow-fs-path-create", allow_fs_path_create_))

    share_info = {
        'id': id_,
        'export_path':  export_path,
        'fs_path':      fs_path,
        'description':  description,
        'restrictions': [r.dictionary() for r in restrictions],
        'present_64_bit_fields_as_32_bit': present_64_bit_fields_as_32_bit,
    }

    return request.rest_request(conninfo, credentials, method, uri,
        body=share_info, if_match=if_match)

@request.request
def nfs_delete_export(conninfo, credentials, id_=None, export_path=None):
    assert [id_, export_path].count(None) == 1

    method = "DELETE"
    uri = str(UriBuilder(path="/v2/nfs/exports/").
        add_path_component(id_ or export_path))

    return request.rest_request(conninfo, credentials, method, uri)
