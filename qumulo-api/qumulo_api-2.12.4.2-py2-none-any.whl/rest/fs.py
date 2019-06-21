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

import time
from qumulo.lib.opts import str_decode
import qumulo.lib.request as request
from qumulo.lib.identity_util import Identity
from qumulo.lib.uri import UriBuilder

@request.request
def read_fs_stats(conninfo, credentials):
    method = "GET"
    uri = "/v1/file-system"
    return request.rest_request(conninfo, credentials, method, unicode(uri))

def ref(path, id_):
    '''
    A "ref" is either a path or file ID. Here, given an argument for both,
    where only one is really present, return the ref.
    '''
    assert (path is not None) ^ (id_ is not None)
    if path is not None and not path.startswith("/"):
        raise ValueError("Path must be absolute.")
    return path if path is not None else unicode(id_)

@request.request
def set_acl(conninfo, credentials, path=None, id_=None, control=None,
        aces=None, if_match=None, posix_special_permissions=None):

    if not control or not aces:
        raise ValueError("Must specify both control flags and ACEs")

    # Don't require POSIX special permissions in the input ACL
    if not posix_special_permissions:
        posix_special_permissions = []

    uri = build_files_uri([ref(path, id_), "info", "acl"])

    if_match = None if not if_match else unicode(if_match)

    config = {
        'aces': list(aces),
        'control': list(control),
        'posix_special_permissions': list(posix_special_permissions)
    }
    method = "PUT"

    return request.rest_request(conninfo, credentials, method, unicode(uri),
        body=config, if_match=if_match)

@request.request
def set_acl_v2(conninfo, credentials, acl, path=None, id_=None, if_match=None):
    uri = build_files_uri([ref(path, id_), "info", "acl"], api_version=2)
    if_match = None if not if_match else unicode(if_match)
    method = "PUT"
    return request.rest_request(conninfo, credentials, method, unicode(uri),
        body=acl, if_match=if_match)

@request.request
def get_attr(conninfo, credentials, path=None, id_=None, snapshot=None):
    """
    This function is deprecated in favor of get_file_attr.
    """
    uri = build_files_uri([ref(path, id_), "info", "attributes"])

    if snapshot:
        uri.add_query_param('snapshot', snapshot)

    method = "GET"
    return request.rest_request(conninfo, credentials, method, unicode(uri))

@request.request
def set_attr(conninfo, credentials, mode, owner, group, modification_time,
        change_time, size=None, creation_time=None, extended_attrs=None,
        path=None, id_=None, if_match=None):
    """
    Sets all file attributes on the specified file system object.
    !!! This function is deprecated in favor of set_file_attr.
    """
    uri = build_files_uri([ref(path, id_), "info", "attributes"])
    if_match = None if not if_match else unicode(if_match)

    method = "PUT"

    config = {
        'mode': unicode(mode),
        'owner': unicode(owner),
        'group': unicode(group),
        'modification_time': unicode(modification_time),
        'change_time': unicode(change_time),
    }

    if size is not None:
        config['size'] = unicode(size)
    if creation_time is not None:
        config['creation_time'] = unicode(creation_time)
    if extended_attrs is not None:
        config['extended_attributes'] = extended_attrs

    return request.rest_request(conninfo, credentials, method, unicode(uri),
        body=config, if_match=if_match)

@request.request
def get_file_attr(
        conninfo,
        credentials,
        id_=None,
        path=None,
        snapshot=None,
        stream_id=None):
    uri = None
    if stream_id:
        uri = build_files_uri(
            [ref(path, id_), 'streams', stream_id, 'attributes'])
    else:
        uri = build_files_uri([ref(path, id_), "info", "attributes"])

    if snapshot:
        uri.add_query_param('snapshot', snapshot)

    method = "GET"
    return request.rest_request(conninfo, credentials, method, unicode(uri))

class FSIdentity(object):
    def __init__(self, id_type, value):
        self.id_type = id_type
        self.value = value

    def __eq__(self, other):
        return self.id_type == other.id_type and self.value == other.value

    def __ne__(self, other):
        return not (self == other)

    def body(self):
        return {
            'id_type': self.id_type,
            'id_value': unicode(self.value),
        }

class NFSUID(FSIdentity):
    def __init__(self, uid):
        super(NFSUID, self).__init__('NFS_UID', uid)

class NFSGID(FSIdentity):
    def __init__(self, gid):
        super(NFSGID, self).__init__('NFS_GID', gid)

class SMBSID(FSIdentity):
    def __init__(self, sid):
        super(SMBSID, self).__init__('SMB_SID', sid)

class LocalUser(FSIdentity):
    def __init__(self, name):
        super(LocalUser, self).__init__('LOCAL_USER', str_decode(name))

class LocalGroup(FSIdentity):
    def __init__(self, name):
        super(LocalGroup, self).__init__('LOCAL_GROUP', str_decode(name))

class InternalIdentity(FSIdentity):
    def __init__(self, name):
        super(InternalIdentity, self).__init__('INTERNAL', name)

@request.request
def set_file_attr(
        conninfo,
        credentials,
        mode=None,
        owner=None,
        group=None,
        size=None,
        creation_time=None,
        modification_time=None,
        change_time=None,
        id_=None,
        extended_attrs=None,
        if_match=None,
        path=None,
        stream_id=None):
    """
    Updates select file attributes on the specified file system object.
    Attributes that are not to be updated should have None specified as
    their values.
    """
    method = "PATCH"

    uri = None
    if stream_id:
        uri = build_files_uri([
            ref(path, id_), 'streams', stream_id, 'attributes'])
    else:
        uri = build_files_uri([ref(path, id_), "info", "attributes"])

    if_match = None if not if_match else unicode(if_match)
    config = {}
    if mode is not None:
        config['mode'] = unicode(mode)

    if owner is not None:
        if isinstance(owner, FSIdentity):
            config['owner_details'] = owner.body()
        else:
            config['owner'] = unicode(owner)

    if group is not None:
        if isinstance(group, FSIdentity):
            config['group_details'] = group.body()
        else:
            config['group'] = unicode(group)

    if size is not None:
        config['size'] = unicode(size)

    if creation_time is not None:
        config['creation_time'] = unicode(creation_time)

    if modification_time is not None:
        config['modification_time'] = unicode(modification_time)

    if change_time is not None:
        config['change_time'] = unicode(change_time)

    if extended_attrs is not None:
        config['extended_attributes'] = extended_attrs

    return request.rest_request(conninfo, credentials, method, unicode(uri),
        body=config, if_match=if_match)

@request.request
def write_file(conninfo, credentials, data_file, path=None, id_=None,
       if_match=None, offset=None, stream_id=None):
    '''
    @param {file} data_file The data to be written to the file
    @param {str}  path      Path to the file. If None, id must not be None
    @param {int}  id        File id of the file. If None, path must not be None
    @param {str}  if_match  If not None, it will be the etag to use
    @param {int}  offset    The position to write in the file.
                            If None, the contents will be completely replaced
    '''
    if stream_id:
        uri = build_files_uri([ref(path, id_), 'streams', stream_id, 'data'])
    else:
        uri = build_files_uri([ref(path, id_), "data"])

    if_match = None if not if_match else unicode(if_match)
    if offset is None:
        method = "PUT"
    else:
        method = "PATCH"
        uri = uri.add_query_param("offset", offset)

    return request.rest_request(
        conninfo,
        credentials,
        method,
        unicode(uri),
        body_file=data_file,
        if_match=if_match,
        request_content_type=request.CONTENT_TYPE_BINARY)

@request.request
def get_acl(conninfo, credentials, path=None, id_=None, snapshot=None):
    uri = build_files_uri([ref(path, id_), "info", "acl"])

    method = "GET"

    if snapshot:
        uri.add_query_param("snapshot", snapshot)

    return request.rest_request(conninfo, credentials, method, unicode(uri))

@request.request
def get_acl_v2(conninfo, credentials, path=None, id_=None, snapshot=None):
    uri = build_files_uri([ref(path, id_), "info", "acl"], api_version=2)
    if snapshot:
        uri.add_query_param("snapshot", snapshot)
    return request.rest_request(conninfo, credentials, "GET", unicode(uri))

@request.request
def read_directory(conninfo, credentials, page_size=None, path=None, id_=None,
        snapshot=None, smb_pattern=None):
    '''
    @param {int} page_size   How many entries to return
    @param {str} path        Directory to read, by path
    @param {int} id_         Directory to read, by ID
    @param {int} snapshot    Snapshot ID of directory to read
    @param {str} smb_pattern SMB style match pattern.
    '''
    uri = build_files_uri([ref(path, id_), "entries"]).append_slash()

    method = "GET"

    if page_size is not None:
        uri.add_query_param("limit", page_size)

    if snapshot:
        uri.add_query_param("snapshot", snapshot)

    if smb_pattern:
        uri.add_query_param("smb-pattern", smb_pattern)

    return request.rest_request(conninfo, credentials, method, unicode(uri))

@request.request
def read_file(conninfo, credentials, file_, path=None, id_=None,
        snapshot=None, offset=None, length=None, stream_id=None):
    uri = None
    if stream_id:
        uri = build_files_uri([ref(path, id_), 'streams', stream_id, 'data'])
    else:
        uri = build_files_uri([ref(path, id_), "data"])

    if snapshot is not None:
        uri.add_query_param('snapshot', snapshot)
    if offset is not None:
        uri.add_query_param('offset', offset)
    if length is not None:
        uri.add_query_param('length', length)

    method = "GET"
    return request.rest_request(conninfo, credentials, method, unicode(uri),
        response_content_type=request.CONTENT_TYPE_BINARY, response_file=file_)

@request.request
def create_file(conninfo, credentials, name, dir_path=None, dir_id=None):
    uri = build_files_uri([ref(dir_path, dir_id), "entries"]).append_slash()

    config = {
        'name': unicode(name).rstrip("/"),
        'action': 'CREATE_FILE'
    }

    method = "POST"
    return request.rest_request(conninfo, credentials, method, unicode(uri),
        body=config)

def validate_major_minor_numbers(file_type, major_minor_numbers):
    if file_type == 'FS_FILE_TYPE_UNIX_BLOCK_DEVICE' or \
        file_type == 'FS_FILE_TYPE_UNIX_CHARACTER_DEVICE':
        if major_minor_numbers is None:
            raise ValueError("major_minor_numbers required for " + file_type)
    elif major_minor_numbers is not None:
        raise ValueError("cannot use major_minor_numbers with " + file_type)

@request.request
def create_unix_file(
        conninfo, credentials, name, file_type, major_minor_numbers=None,
        dir_path=None, dir_id=None):
    uri = build_files_uri([ref(dir_path, dir_id), "entries"]).append_slash()

    config = {
        'name': unicode(name).rstrip("/"),
        'action': 'CREATE_UNIX_FILE',
        'unix_file_type': file_type,
    }

    validate_major_minor_numbers(file_type, major_minor_numbers)

    if major_minor_numbers is not None:
        config['major_minor_numbers'] = major_minor_numbers

    method = "POST"
    return request.rest_request(conninfo, credentials, method, unicode(uri),
        body=config)

@request.request
def create_directory(conninfo, credentials, name, dir_path=None, dir_id=None):
    uri = build_files_uri([ref(dir_path, dir_id), "entries"]).append_slash()

    config = {
        'name': unicode(name),
        'action': 'CREATE_DIRECTORY'
    }

    method = "POST"
    return request.rest_request(conninfo, credentials, method, unicode(uri),
        body=config)

@request.request
def create_symlink(conninfo, credentials, name, target, dir_path=None,
                   dir_id=None, target_type=None):
    uri = build_files_uri([ref(dir_path, dir_id), "entries"]).append_slash()

    config = {
        'name': unicode(name).rstrip("/"),
        'old_path': unicode(target),
        'action': 'CREATE_SYMLINK'
    }
    if target_type is not None:
        config['symlink_target_type'] = target_type

    method = "POST"
    return request.rest_request(conninfo, credentials, method, unicode(uri),
        body=config)

@request.request
def create_link(conninfo, credentials, name, target, dir_path=None,
                dir_id=None):
    uri = build_files_uri([ref(dir_path, dir_id), "entries"]).append_slash()

    config = {
        'name': unicode(name).rstrip("/"),
        'old_path': unicode(target),
        'action': 'CREATE_LINK'
    }

    method = "POST"
    return request.rest_request(conninfo, credentials, method, unicode(uri),
        body=config)

@request.request
def rename(conninfo, credentials, name, source, dir_path=None, dir_id=None,
           clobber=False):
    uri = build_files_uri([ref(dir_path, dir_id), "entries"]).append_slash()

    config = {
        'name': unicode(name).rstrip("/"),
        'old_path': unicode(source),
        'action': 'RENAME',
        'clobber': clobber
    }

    method = "POST"
    return request.rest_request(conninfo, credentials, method, unicode(uri),
        body=config)

@request.request
def delete(conninfo, credentials, path=None, id_=None):
    uri = build_files_uri([ref(path, id_)])
    method = "DELETE"
    return request.rest_request(conninfo, credentials, method, unicode(uri))

@request.request
def delete_tree(conninfo, credentials, path=None, id_=None):
    uri = build_files_uri([ref(path, id_), "delete-tree"])
    method = "POST"
    return request.rest_request(conninfo, credentials, method, unicode(uri))

@request.request
def tree_delete_status(conninfo, credentials, path=None, id_=None):
    uri = build_files_uri([ref(path, id_), "delete-tree", "status"])
    method = "GET"
    return request.rest_request(conninfo, credentials, method, unicode(uri))

@request.request
def read_dir_aggregates(conninfo, credentials, path=None,
        recursive=False, max_entries=None, max_depth=None, order_by=None,
        id_=None, snapshot=None):
    method = "GET"

    aggregate = "recursive-aggregates" if recursive else "aggregates"
    uri = build_files_uri([ref(path, id_), aggregate]).append_slash()

    if max_entries is not None:
        uri.add_query_param('max-entries', max_entries)
    if max_depth is not None:
        uri.add_query_param('max-depth', max_depth)
    if order_by is not None:
        uri.add_query_param('order-by', order_by)
    if snapshot is not None:
        uri.add_query_param('snapshot', snapshot)
    return request.rest_request(conninfo, credentials, method, unicode(uri))

@request.request
def get_file_samples(conninfo, credentials, path, count, by_value, id_=None):
    method = "GET"

    uri = build_files_uri([ref(path, id_), 'sample']).append_slash()
    uri.add_query_param('by-value', by_value)
    uri.add_query_param('limit', count)

    return request.rest_request(conninfo, credentials, method, unicode(uri))

@request.request
def resolve_paths(conninfo, credentials, ids, snapshot=None):
    method = "POST"
    uri = build_files_uri(["resolve"])

    if snapshot:
        uri.add_query_param('snapshot', snapshot)

    return request.rest_request(
        conninfo, credentials, method, unicode(uri), body=ids)

@request.request
def punch_hole(
        conninfo,
        credentials,
        offset,
        size,
        path=None,
        id_=None,
        if_match=None,
        stream_id=None):

    if stream_id:
        uri = build_files_uri(
            [ref(path, id_), 'streams', stream_id, 'punch-hole'])
    else:
        uri = build_files_uri([ref(path, id_), 'punch-hole'])

    if_match = None if not if_match else unicode(if_match)
    body = {'offset': unicode(offset), 'size': unicode(size)}
    return request.rest_request(
        conninfo,
        credentials,
        'POST',
        unicode(uri),
        body=body,
        if_match=if_match)

# __        __    _ _
# \ \      / /_ _(_) |_ ___ _ __ ___
#  \ \ /\ / / _` | | __/ _ \ '__/ __|
#   \ V  V / (_| | | ||  __/ |  \__ \
#    \_/\_/ \__,_|_|\__\___|_|  |___/
#  FIGLET: Waiters
#
VALID_WAITER_PROTO_TYPE_COMBINATIONS = [
    ('nlm', 'byte-range'),
]

@request.request
def list_waiters_by_file(
        conninfo,
        credentials,
        protocol,
        lock_type,
        file_path=None,
        file_id=None,
        snapshot_id=None,
        limit=None,
        after=None):
    assert (protocol, lock_type) in VALID_WAITER_PROTO_TYPE_COMBINATIONS
    uri = build_files_uri(
        [ref(file_path, file_id), 'locks', protocol, lock_type, 'waiters'],
        append_slash=True)
    if limit:
        uri.add_query_param("limit", limit)
    if after:
        uri.add_query_param("after", after)
    if snapshot_id:
        uri.add_query_param("snapshot", snapshot_id)
    return request.rest_request(conninfo, credentials, "GET", unicode(uri))

@request.request
def list_waiters_by_client(
        conninfo,
        credentials,
        protocol,
        lock_type,
        owner_name=None,
        owner_address=None,
        limit=None,
        after=None):
    assert (protocol, lock_type) in VALID_WAITER_PROTO_TYPE_COMBINATIONS
    uri = build_files_uri(['locks', protocol, lock_type, 'waiters'],
        append_slash=True)
    if limit:
        uri.add_query_param("limit", limit)
    if after:
        uri.add_query_param("after", after)
    if owner_name:
        uri.add_query_param("owner_name", owner_name)
    if owner_address:
        uri.add_query_param("owner_address", owner_address)
    return request.rest_request(conninfo, credentials, "GET", unicode(uri))

@request.request
def list_all_waiters_by_file(
        conninfo,
        credentials,
        protocol,
        lock_type,
        file_path=None,
        file_id=None,
        snapshot_id=None,
        limit=1000):
    '''
    Re-assembles the paginated list of lock waiters for the given file.
    '''
    result = list_waiters_by_file(conninfo, credentials, protocol, lock_type,
                                file_path, file_id, snapshot_id, limit)
    return _get_remaining_pages_for_list_lock_requests(
            conninfo, credentials, result, limit, req_type = 'waiters')

@request.request
def list_all_waiters_by_client(
        conninfo,
        credentials,
        protocol,
        lock_type,
        owner_name=None,
        owner_address=None,
        limit=1000):
    '''
    Re-assembles the paginated list of lock waiters for the given client.
    '''
    result = list_waiters_by_client(conninfo, credentials, protocol, lock_type,
        owner_name, owner_address, limit)
    return _get_remaining_pages_for_list_lock_requests(
            conninfo, credentials, result, limit, req_type = 'waiters')

#  _               _
# | |    ___   ___| | _____
# | |   / _ \ / __| |/ / __|
# | |__| (_) | (__|   <\__ \
# |_____\___/ \___|_|\_\___/
# FIGLET: Locks

VALID_LOCK_PROTO_TYPE_COMBINATIONS = [
    ('smb', 'byte-range'),
    ('smb', 'share-mode'),
    ('nlm', 'byte-range'),
]

@request.request
def list_locks_by_file(
        conninfo,
        credentials,
        protocol,
        lock_type,
        file_path=None,
        file_id=None,
        snapshot_id=None,
        limit=None,
        after=None):
    assert (protocol, lock_type) in VALID_LOCK_PROTO_TYPE_COMBINATIONS
    uri = build_files_uri(
        [ref(file_path, file_id), 'locks', protocol, lock_type],
        append_slash=True)
    if limit:
        uri.add_query_param("limit", limit)
    if after:
        uri.add_query_param("after", after)
    if snapshot_id:
        uri.add_query_param("snapshot", snapshot_id)
    return request.rest_request(conninfo, credentials, "GET", unicode(uri))

@request.request
def list_locks_by_client(
        conninfo,
        credentials,
        protocol,
        lock_type,
        owner_name=None,
        owner_address=None,
        limit=None,
        after=None):
    assert (protocol, lock_type) in VALID_LOCK_PROTO_TYPE_COMBINATIONS
    uri = build_files_uri(['locks', protocol, lock_type], append_slash=True)
    if limit:
        uri.add_query_param("limit", limit)
    if after:
        uri.add_query_param("after", after)
    if owner_name:
        uri.add_query_param("owner_name", owner_name)
    if owner_address:
        uri.add_query_param("owner_address", owner_address)
    return request.rest_request(conninfo, credentials, "GET", unicode(uri))

def _get_remaining_pages_for_list_lock_requests(
        conninfo, credentials, result, limit, req_type = 'grants'):
    '''
    Given the first page of a lock grant listing, retrieves all subsequent
    pages, and returns the complete grant list.
    @p req_type can either be 'grants' or 'waiters'
    '''
    full_list = result.data[req_type]
    while len(result.data[req_type]) == limit:
        # If we got a full page, there are probably more pages.  Waiting for
        # an empty page would also be reasonable, but carries the risk of
        # never terminating if clients are frequently taking new locks.
        result = request.rest_request(
            conninfo, credentials, "GET", result.data['paging']['next'])
        full_list += result.data[req_type]
    return full_list

@request.request
def list_all_locks_by_file(
        conninfo,
        credentials,
        protocol,
        lock_type,
        file_path=None,
        file_id=None,
        snapshot_id=None,
        limit=1000):
    '''
    Re-assembles the paginated list of lock grants for the given file.
    '''
    result = list_locks_by_file(conninfo, credentials, protocol, lock_type,
                                file_path, file_id, snapshot_id, limit)
    return _get_remaining_pages_for_list_lock_requests(
            conninfo, credentials, result, limit)

@request.request
def list_all_locks_by_client(
        conninfo,
        credentials,
        protocol,
        lock_type,
        owner_name=None,
        owner_address=None,
        limit=1000):
    '''
    Re-assembles the paginated list of lock grants for the given client.
    '''
    result = list_locks_by_client(conninfo, credentials, protocol, lock_type,
        owner_name, owner_address, limit)
    return _get_remaining_pages_for_list_lock_requests(
            conninfo, credentials, result, limit)

@request.request
def release_nlm_locks_by_client(
        conninfo,
        credentials,
        owner_name=None,
        owner_address=None):
    assert owner_name or owner_address
    protocol, lock_type = 'nlm', 'byte-range'
    uri = build_files_uri(['locks', protocol, lock_type], append_slash=True)
    if owner_name:
        uri.add_query_param("owner_name", owner_name)
    if owner_address:
        uri.add_query_param("owner_address", owner_address)
    return request.rest_request(conninfo, credentials, "DELETE", unicode(uri))

@request.request
def release_nlm_lock(
        conninfo,
        credentials,
        offset,
        size,
        owner_id,
        file_path=None,
        file_id=None,
        snapshot=None):
    protocol, lock_type = 'nlm', 'byte-range'
    uri = build_files_uri(
        [ref(file_path, file_id), 'locks', protocol, lock_type],
        append_slash=True)
    uri.add_query_param("offset", offset)
    uri.add_query_param("size", size)
    uri.add_query_param("owner_id", owner_id)
    if snapshot is not None:
        uri.add_query_param("snapshot", snapshot)
    return request.rest_request(conninfo, credentials, "DELETE", unicode(uri))

#  _   _      _
# | | | | ___| |_ __   ___ _ __ ___
# | |_| |/ _ \ | '_ \ / _ \ '__/ __|
# |  _  |  __/ | |_) |  __/ |  \__ \
# |_| |_|\___|_| .__/ \___|_|  |___/
#              |_|
#
def build_files_uri(components, append_slash=False, api_version=1):
    uri = UriBuilder(path="/v{}/files".format(api_version))

    if components:
        for component in components:
            uri.add_path_component(component)

    if append_slash:
        uri.append_slash()

    return uri

# Return an iterator that reads an entire directory. Each iteration returns a
# page of files, which will be the specified page size or less.
@request.request
def read_entire_directory(conninfo, credentials, page_size=None, path=None,
        id_=None, snapshot=None, smb_pattern=None):
    # Perform initial read_directory normally.
    result = read_directory(conninfo, credentials, page_size=page_size,
        path=path, id_=id_, snapshot=snapshot, smb_pattern=smb_pattern)
    next_uri = result.data['paging']['next']
    yield result

    while next_uri != '':
        # Perform raw read_directory with paging URI.
        result = request.rest_request(conninfo, credentials, "GET", next_uri)
        next_uri = result.data['paging']['next']
        yield result

# Return an iterator that reads an entire directory. Each iteration returns a
# page of files. Any fs_no_such_entry_error returned is logged and ignored,
# ending the iteration.
def read_entire_directory_and_ignore_not_found(
    conninfo, credentials, page_size=None, path=None, id_=None):
    try:
        for result in read_entire_directory(
                conninfo, credentials, page_size, path, id_):
            yield result
    except request.RequestError as e:
        if e.status_code != 404 or e.error_class != 'fs_no_such_entry_error':
            raise

# Return an iterator that walks a file system tree depth-first and pre-order
@request.request
def tree_walk_preorder(conninfo, credentials, path):
    path = unicode(path)

    def call_read_dir(conninfo, credentials, path):
        for result in read_entire_directory_and_ignore_not_found(
                conninfo, credentials, path=path):
            if 'files' in result.data:
                for f in result.data['files']:
                    yield request.RestResponse(f, result.etag)

                    if f['type'] == 'FS_FILE_TYPE_DIRECTORY':
                        for ff in call_read_dir(conninfo, credentials,
                                                f['path']):
                            yield ff

    result = get_file_attr(conninfo, credentials, path=path)
    yield result

    for f in call_read_dir(conninfo, credentials, path):
        yield f

# Return an iterator that walks a file system tree depth-first and post-order
@request.request
def tree_walk_postorder(conninfo, credentials, path):
    path = unicode(path)

    def call_read_dir(conninfo, credentials, path):
        for result in read_entire_directory_and_ignore_not_found(
                conninfo, credentials, path=path):
            if 'files' in result.data:
                for f in result.data['files']:
                    if f['type'] == 'FS_FILE_TYPE_DIRECTORY':
                        for ff in call_read_dir(conninfo, credentials,
                                                f['path']):
                            yield ff
                    yield request.RestResponse(f, result.etag)

    result = get_file_attr(conninfo, credentials, path=path)

    for f in call_read_dir(conninfo, credentials, path):
        yield f

    yield result

@request.request
def delete_tree_sync(
        conninfo, credentials, path=None, id_=None, poll_interval=0.1):
    '''
    Call tree-delete on a path and wait for the tree-delete process to complete.
    '''
    delete_tree(conninfo, credentials, path=path, id_=id_)
    while True:
        try:
            tree_delete_status(conninfo, credentials, path=path, id_=id_)
        except request.RequestError as e:
            if e.error_class in {'fs_no_such_entry_error',
                                 'fs_no_such_inode_error',
                                 'http_not_found_error'}:
                break
            else:
                raise

        time.sleep(poll_interval)

@request.request
def acl_explain_posix_mode(conninfo, credentials, path=None, id_=None):
    method = "POST"

    uri = build_files_uri([ref(path, id_), 'info', 'acl', 'explain-posix-mode'])

    return request.rest_request(conninfo, credentials, method, unicode(uri))

@request.request
def acl_explain_chmod(conninfo, credentials, path=None, id_=None, mode=None):
    method = "POST"

    uri = build_files_uri([ref(path, id_), 'info', 'acl', 'explain-set-mode'])

    return request.rest_request(
        conninfo, credentials, method, unicode(uri), body={ 'mode': mode })

@request.request
def acl_explain_rights(
        conninfo, credentials, user, group, ids=None, path=None, id_=None):
    method = "POST"
    '''
    @param {str}  user      User for whom to explain rights.
    @param {str}  path      Path to the file. If None, id must not be None
    @param {int}  id        File id of the file. If None, path must not be None
    @param {str}  group     User's primary group.
    @param {list} ids       User's additional groups and related identities.
    '''

    uri = build_files_uri([ref(path, id_), 'info', 'acl', 'explain-rights'])

    payload = { 'user': Identity(user).dictionary() }
    if group:
        payload['primary_group'] = Identity(group).dictionary()
    if ids:
        payload['auxiliary_identities'] = [Identity(i).dictionary()
            for i in ids]

    return request.rest_request(
        conninfo, credentials, method, unicode(uri), body=payload)

@request.request
def get_permissions_settings(conninfo, credentials):
    return request.rest_request(
        conninfo, credentials, "GET", "/v1/file-system/settings/permissions")

@request.request
def set_permissions_settings(conninfo, credentials, mode):
    '''
    @param {str} mode  NATIVE, _DEPRECATED_MERGED_V1, or CROSS_PROTOCOL
    '''
    return request.rest_request(conninfo, credentials, "PUT",
        "/v1/file-system/settings/permissions", body={'mode': mode})
