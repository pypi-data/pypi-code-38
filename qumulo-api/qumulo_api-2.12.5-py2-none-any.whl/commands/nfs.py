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

'''
NFS export commands
'''

import json
import sys

import qumulo.lib.opts
import qumulo.lib.util as util
import qumulo.rest.nfs as nfs
import qumulo.rest.users as users

from qumulo.rest.nfs import NFSRestriction
from qumulo.rest.nfs import NFSExportRestriction

ADD_MODIFY_SHARE_RESTRICTION_HELP = ('''
    Path to local file containing the restrictions in JSON format.
    user_mapping can be "none"|"root"|"all".
    map_to_user_id may be "guest"|"admin"|"<integer_id>".
    Example JSON:
    { "restrictions" : [ {
    "read_only" : true,
    "host_restrictions" : [ "1.2.3.1", "1.2.3.2" ],
    "user_mapping" : "root",
    "map_to_user_id" : "guest" },
    {<another_restriction>} ] } ''')

def convert_nfs_user_mapping(name):
    convert = {
        'none':         'NFS_MAP_NONE',
        'root':         'NFS_MAP_ROOT',
        'all':          'NFS_MAP_ALL',
        'nfs_map_none': 'NFS_MAP_NONE',
        'nfs_map_root': 'NFS_MAP_ROOT',
        'nfs_map_all':  'NFS_MAP_ALL',
    }

    if name.lower() not in convert:
        raise ValueError('%s is not one of none, root, or all' % (name))
    return convert[name.lower()]

def process_user_mapping(user_mapping, map_to_user_id):
    user_mapping = convert_nfs_user_mapping(user_mapping)
    if user_mapping != 'NFS_MAP_NONE' and map_to_user_id == '0':
        raise ValueError('user_mapping ' + user_mapping +
            ' requires map_to_user_id')
    if user_mapping == 'NFS_MAP_NONE' and map_to_user_id != '0':
        raise ValueError('map_to_user_id is only valid when mapping an user ' +
            '(user_mapping is not NONE). If user_mapping is NONE, remove ' +
            'map_to_user_id or make it "0".')
    return user_mapping

def parse_nfs_restrictions_file(conninfo, credentials, path):
    # Parse JSON file.
    with open(path) as f:
        contents = f.read()
        try:
            restrictions = json.loads(contents)
        except ValueError as e:
            raise ValueError('Error parsing JSON restrictions file ' + str(e))

    # Validate the restrictions are well formed, and create the
    # NFSRestriction object.
    nfs_restrictions = list()
    for r in restrictions['restrictions']:
        # Get read-only.
        read_only = r.get('read_only', False)

        # Process host restrictions.
        host_restrictions = r.get('host_restrictions', [])

        # Process user mapping values.
        try:
            user_mapping = process_user_mapping(r.get('user_mapping', 'none'),
                r.get('map_to_user_id', '0'))
        except ValueError as e:
            raise ValueError('When trying to process the following ' +
                'restriction: ' + str(r) + ', this error was thrown: ' + str(e))

        # Allow either auth_id or user name.
        user_id = users.get_user_id(conninfo, credentials,
            r.get('map_to_user_id', '0'))

        # Add the NFSRestriction to the list.
        nfs_restrictions.append(
            NFSRestriction({
                'read_only': read_only,
                'host_restrictions': host_restrictions,
                'user_mapping': user_mapping,
                'map_to_user_id': str(user_id.data)
            }))

    # Return the list of restrictions.
    return nfs_restrictions

class NFSListSharesCommand(qumulo.lib.opts.Subcommand):
    NAME = "nfs_list_shares"
    DESCRIPTION = "List all NFS shares [DEPRECATED]"

    @staticmethod
    def main(conninfo, credentials, _args):
        sys.stderr.write(
            'Warning: nfs_list_shares is deprecated. See nfs_list_exports.\n')
        print nfs.nfs_list_shares(conninfo, credentials)

class NFSAddShareCommand(qumulo.lib.opts.Subcommand):
    NAME = "nfs_add_share"
    DESCRIPTION = "Add a new NFS share [DEPRECATED]"

    @staticmethod
    def options(parser):
        parser.add_argument("--export-path", type=str, default=None,
            required=True, help="NFS Export path")
        parser.add_argument("--fs-path", type=str, default=None, required=True,
            help="File system path")
        parser.add_argument("--description", type=str, default='',
            help="Description of this export")
        # Require either 'no-restrictions' or the restrictions file.
        restriction_arg = parser.add_mutually_exclusive_group(required=True)
        restriction_arg.add_argument("--no-restrictions", action="store_true",
            default=False, help='Specify no restrictions for this share.')
        restriction_arg.add_argument("--restrictions", type=str, default=None,
            metavar='JSON_FILE_PATH', required=False,
            help=ADD_MODIFY_SHARE_RESTRICTION_HELP)
        parser.add_argument("--create-fs-path", action="store_true",
            help="Creates the specified file system path if it does not exist")

    @staticmethod
    def main(conninfo, credentials, args):
        sys.stderr.write(
            'Warning: nfs_add_share is deprecated. See nfs_add_exports.\n')
        if args.restrictions:
            restrictions = parse_nfs_restrictions_file(conninfo, credentials,
                args.restrictions)
        else:
            restrictions = [NFSRestriction.create_default()]

        print nfs.nfs_add_share(conninfo, credentials,
            args.export_path, args.fs_path, args.description, restrictions,
            args.create_fs_path)

class NFSListShareCommand(qumulo.lib.opts.Subcommand):
    NAME = "nfs_list_share"
    DESCRIPTION = "List a share [DEPRECATED]"

    @staticmethod
    def options(parser):
        parser.add_argument("--id", type=str, default=None, required=True,
            help="ID of share to list")

    @staticmethod
    def main(conninfo, credentials, args):
        sys.stderr.write(
            'Warning: nfs_list_share is deprecated. See nfs_get_export.\n')
        print nfs.nfs_list_share(conninfo, credentials, args.id)

class NFSModShareCommand(qumulo.lib.opts.Subcommand):
    NAME = "nfs_mod_share"
    DESCRIPTION = "Modify a share [DEPRECATED]"

    @staticmethod
    def options(parser):
        parser.add_argument("--id", type=str, default=None, required=True,
            help="ID of share to modify")
        parser.add_argument("--export-path", type=str, default=None,
            help="Change NFS export path")
        parser.add_argument("--fs-path", type=str, default=None,
            help="Change file system path")
        parser.add_argument("--description", type=str, default=None,
            help="Description of this export")
        # Do not require a restrictions argument, it will preserve the existing
        # ones.
        restriction_arg = parser.add_mutually_exclusive_group(required=False)
        restriction_arg.add_argument("--no-restrictions", action="store_true",
            default=False, help='Specify no restrictions for this share.')
        restriction_arg.add_argument("--restrictions", type=str, default=None,
            metavar='JSON_FILE_PATH', required=False,
            help=ADD_MODIFY_SHARE_RESTRICTION_HELP)
        parser.add_argument("--create-fs-path", action="store_true",
            help="Creates the specified file system path if it does not exist")

    @staticmethod
    def main(conninfo, credentials, args):
        sys.stderr.write(
            'Warning: nfs_mod_share is deprecated. See nfs_mod_export.\n')

        # Get existing share
        share_info = {}
        share_info, share_info['if_match'] = \
            nfs.nfs_list_share(conninfo, credentials, args.id)

        # Modify share
        share_info['id_'] = share_info['id']
        share_info['allow_fs_path_create'] = args.create_fs_path
        del share_info['id']
        if args.export_path is not None:
            share_info['export_path'] = args.export_path
        if args.fs_path is not None:
            share_info['fs_path'] = args.fs_path
        if args.description is not None:
            share_info['description'] = args.description

        # Overwrite the NFS restrictions from JSON file.
        if args.restrictions:
            share_info['restrictions'] = parse_nfs_restrictions_file(
                conninfo, credentials, args.restrictions)
        elif args.no_restrictions:
            # Modify the share's restrictions to be the default ones (no
            # restrictions).
            share_info['restrictions'] = [NFSRestriction.create_default()]
        else:
            # If no restrictions were specified and the user didn't set the
            # --no-restrictions flag, let's preserve the ones that
            # were originally set for this share. However, we need to re-pack
            # them to be of type "NFSRestriction", in order to keep the REST
            # client consistent.
            share_info['restrictions'] = \
                [NFSRestriction(r) for r in share_info['restrictions']]

        print nfs.nfs_modify_share(conninfo, credentials,
            **share_info)

class NFSDeleteShareCommand(qumulo.lib.opts.Subcommand):
    NAME = "nfs_delete_share"
    DESCRIPTION = "Delete a share [DEPRECATED]"

    @staticmethod
    def options(parser):
        parser.add_argument("--id", type=str, default=None, required=True,
            help="ID of share to delete")

    @staticmethod
    def main(conninfo, credentials, args):
        sys.stderr.write(
            'Warning: nfs_delete_share is deprecated. See nfs_delete_export.\n')
        nfs.nfs_delete_share(conninfo, credentials, args.id)
        print "Share has been deleted."

# __     ______     ____                                          _
# \ \   / /___ \   / ___|___  _ __ ___  _ __ ___   __ _ _ __   __| |___
#  \ \ / /  __) | | |   / _ \| '_ ` _ \| '_ ` _ \ / _` | '_ \ / _` / __|
#   \ V /  / __/  | |__| (_) | | | | | | | | | | | (_| | | | | (_| \__ \
#    \_/  |_____|  \____\___/|_| |_| |_|_| |_| |_|\__,_|_| |_|\__,_|___/
# Figlet: v2 commands

ADD_MODIFY_RESTRICTION_HELP = ('''
    Path to local file containing the restrictions in JSON format.
    user_mapping can be "none"|"root"|"all".
    map_to_user may be "{ "id_type": "LOCAL_USER", "id_value": "<integer_id>" }"
     or "{ "id_type": "NFS_UID", "id_value": "<integer_id>" }".
    map_to_group may be "{ "id_type": "NFS_GID", "id_value": "<integer_id>".
    If user_mapping is not "none", then either specify map_to_user as a
    local user or specify both map_to_user and map_to_group as NFS user/group.
    Example JSON:
    { "restrictions" : [
        {
            "read_only" : true,
            "host_restrictions" : [ "1.2.3.1", "1.2.3.2" ],
            "user_mapping" : "root",
            "map_to_user": {
                "id_type" : "LOCAL_USER",
                "id_value" : "500"
            }
        },
        {
            "read_only" : true,
            "host_restrictions" : [],
            "user_mapping" : "all",
            "map_to_user" :{
                "id_type" : "NFS_UID",
                "id_value" : "500"
            },
            "map_to_group": {
                "id_type" : "NFS_GID",
                "id_value" : "501"
            }
        } ]
    } ''')

def parse_nfs_export_restrictions_file(path):
    with open(path) as f:
        contents = f.read()
        try:
            restrictions = json.loads(contents)
        except ValueError as e:
            raise ValueError('Error parsing JSON restrictions file ' + str(e) +
                'file content' +  contents)
    return parse_nfs_export_restrictions(restrictions['restrictions'])

def parse_nfs_export_restrictions(restrictions):
    nfs_export_restrictions = list()
    for r in restrictions:
        read_only = r.get('read_only', False)
        require_privileged_port = r.get('require_privileged_port', False)

        host_restrictions = r.get('host_restrictions', [])

        try:
            user_mapping = convert_nfs_user_mapping(
                                r.get('user_mapping', 'none'))

            restriction = NFSExportRestriction({
                'read_only': read_only,
                'host_restrictions': host_restrictions,
                'user_mapping': user_mapping,
                'require_privileged_port': require_privileged_port
            })
            if (user_mapping == 'NFS_MAP_NONE'):
                nfs_export_restrictions.append(restriction)
                continue

            user = r.get('map_to_user')

            if (user.get('id_type') == 'NFS_UID') ^ ('map_to_group' in r):
                raise ValueError('Restriction should either specify map_to_user'
                ' with an NFS uid and map_to_group with an NFS gid, or specify '
                'map_to_user with a local user id.')

            restriction['map_to_user'] = \
                {
                    'id_type': user.get('id_type'),
                    'id_value': user.get('id_value')
                }
            if 'map_to_group' in r:
                group = r.get('map_to_group')
                restriction['map_to_group'] = \
                    {
                        'id_type': group.get('id_type'),
                        'id_value': group.get('id_value')
                    }
        except (ValueError, AttributeError) as e:
            raise ValueError('When trying to process the following ' +
                'restriction: ' + str(r) + ', this error was thrown: ' + str(e))

        nfs_export_restrictions.append(restriction)

    return nfs_export_restrictions

class NFSListExportsCommand(qumulo.lib.opts.Subcommand):
    NAME = "nfs_list_exports"
    DESCRIPTION = "List all NFS exports"

    @staticmethod
    def options(parser):
        parser.add_argument("--json", default=False, action='store_true',
            help="Print raw response JSON.")

    @staticmethod
    def main(conninfo, credentials, args):
        response = nfs.nfs_list_exports(conninfo, credentials)
        if args.json:
            print response
            return

        exports, _etag = response
        print util.tabulate(
            [[e['id'], e['export_path'], e['fs_path'], e['description']]
                for e in exports],
            ['ID', 'Export Path', 'FS Path', 'Description'])

def str_decode(arg):
    '''
    Custom argparse type for decoding based on stdin-specific encoding. If stdin
    does not provide an encoding (e.g. is a pipe), then default to utf-8 for
    the sake of doing something relatively sane.
    '''
    return unicode(arg, sys.stdin.encoding or 'utf-8')

def nfs_restriction_to_etc_exports_opts(restriction):
    opts = list()
    opts.append(u'ro' if restriction['read_only'] else u'rw')
    opts.append(
        u'secure' if restriction['require_privileged_port'] else u'insecure')
    have_map_to = False
    if restriction['user_mapping'] == 'NFS_MAP_NONE':
        opts.append(u'no_root_squash')
    elif restriction['user_mapping'] == 'NFS_MAP_ROOT':
        opts.append(u'root_squash')
        have_map_to = True
    else:
        assert restriction['user_mapping'] == 'NFS_MAP_ALL', \
            'Unexpected user mapping type: {}'.format(
                restriction['user_mapping'])
        opts.append(u'all_squash')
        have_map_to = True

    if have_map_to and restriction['map_to_user']['id_type'] == 'LOCAL_USER':
        # If mapping to a local user, there is no map_to_group (instead the
        # user's primary group is used).  There's no direct equivalent in
        # /etc/exports, so make up a stylistically-similar one:
        opts.append(u'anonlocal={}'.format(
            restriction['map_to_user']['id_value']))
    elif have_map_to and restriction['map_to_user']['id_type'] == 'NFS_UID':
        opts.append(u'anonuid={}'.format(
            restriction['map_to_user']['id_value']))
        opts.append(u'anongid={}'.format(
            restriction['map_to_group']['id_value']))
    else:
        assert not have_map_to, \
            'Unexpected map_to_user type: {}'.format(
                restriction['map_to_user']['id_type'])

    return opts

def pretty_print_export(export, print_json):
    if print_json:
        print json.dumps(export, indent=4)
        return

    print u'ID:          {}'.format(export['id'])
    print u'Export Path: {}'.format(export['export_path'])
    print u'FS Path:     {}'.format(export['fs_path'])
    print u'Description: {}'.format(export['description'])
    print u'32 bit mode: {}'.format(
        export['present_64_bit_fields_as_32_bit'])
    print u'Host Access:'
    access_table = []
    for i, r in enumerate(export['restrictions'], start=1):
        access_table.append([
            i,
            ', '.join(r['host_restrictions']) if r['host_restrictions']
                else '*',
            ', '.join(nfs_restriction_to_etc_exports_opts(r))])
    print util.tabulate(access_table, ['ID', 'Hosts', 'Access Options'])

class NFSGetExportCommand(qumulo.lib.opts.Subcommand):
    NAME = "nfs_get_export"
    DESCRIPTION = "Get an export"

    @staticmethod
    def options(parser):
        export = parser.add_mutually_exclusive_group(required=True)
        export.add_argument("--id", type=str, default=None,
            help="ID of export to list")
        export.add_argument("--export-path", type=str_decode, default=None,
            help="Path of export to list")

        parser.add_argument("--json", default=False, action='store_true',
            help="Print raw response JSON.")

    @staticmethod
    def main(conninfo, credentials, args):
        response = nfs.nfs_get_export(conninfo, credentials,
            args.id, args.export_path)
        pretty_print_export(response[0], args.json)

class NFSAddExportCommand(qumulo.lib.opts.Subcommand):
    NAME = "nfs_add_export"
    DESCRIPTION = "Add a new NFS export"

    @staticmethod
    def options(parser):
        parser.add_argument("--export-path", type=str_decode, default=None,
            required=True, help="NFS Export path")
        parser.add_argument("--fs-path", type=str_decode,
            default=None, required=True,
            help="File system path")
        parser.add_argument("--description", type=str_decode, default='',
            help="Description of this export")

        restriction_arg = parser.add_mutually_exclusive_group(required=True)
        restriction_arg.add_argument("--no-restrictions", action="store_true",
            default=False, help='Specify no restrictions for this export.')
        restriction_arg.add_argument("--restrictions", type=str, default=None,
            metavar='JSON_FILE_PATH', required=False,
            help= ADD_MODIFY_RESTRICTION_HELP)
        parser.add_argument("--create-fs-path", action="store_true",
            help="Creates the specified file system path if it does not exist")
        parser.add_argument(
            "--present-64-bit-fields-as-32-bit",
            type=util.bool_from_string,
            metavar='{true,false}',
            default=False,
            help="Provides 32-bit compatibility on this share. Presents all "
                 "64-bit NFS fields as 32-bit.")

    @staticmethod
    def main(conninfo, credentials, args):
        if args.restrictions:
            restrictions = parse_nfs_export_restrictions_file(args.restrictions)
        else:
            restrictions = [NFSExportRestriction.create_default()]

        print nfs.nfs_add_export(
            conninfo,
            credentials,
            args.export_path,
            args.fs_path,
            args.description,
            restrictions,
            allow_fs_path_create=args.create_fs_path,
            present_64_bit_fields_as_32_bit=
                args.present_64_bit_fields_as_32_bit)

class NFSModExportCommand(qumulo.lib.opts.Subcommand):
    NAME = "nfs_mod_export"
    DESCRIPTION = "Modify an export"

    @staticmethod
    def options(parser):
        export = parser.add_mutually_exclusive_group(required=True)
        export.add_argument("--id", type=str, default=None,
            help="ID of export to modify")
        export.add_argument("--export-path", type=str_decode, default=None,
            help="Path of export to modify")

        parser.add_argument("--new-export-path", type=str_decode, default=None,
            help="Change NFS export path")
        parser.add_argument("--fs-path", type=str_decode, default=None,
            help="Change file system path")
        parser.add_argument("--description", type=str_decode, default=None,
            help="Description of this export")
        # Do not require a restrictions argument, it will preserve the existing
        # ones.
        restriction_arg = parser.add_mutually_exclusive_group(required=False)
        restriction_arg.add_argument("--no-restrictions", action="store_true",
            default=False, help='Specify no restrictions for this export.')
        restriction_arg.add_argument("--restrictions", type=str, default=None,
            metavar='JSON_FILE_PATH', required=False,
            help=ADD_MODIFY_RESTRICTION_HELP)
        parser.add_argument("--create-fs-path", action="store_true",
            help="Creates the specified file system path if it does not exist")
        parser.add_argument(
            "--present-64-bit-fields-as-32-bit",
            type=util.bool_from_string,
            metavar='{true,false}',
            default=None,
            help="Provides 32-bit compatibility on this share. Presents all "
                 "64-bit NFS fields as 32-bit.")

    @staticmethod
    def main(conninfo, credentials, args):
        response = nfs.nfs_get_export(
            conninfo, credentials, args.id, args.export_path)

        export_info = {}
        export_info, export_info['if_match'] = response

        export_info['id_'] = export_info['id']
        export_info['allow_fs_path_create'] = args.create_fs_path
        if args.present_64_bit_fields_as_32_bit is not None:
            export_info['present_64_bit_fields_as_32_bit'] = \
                args.present_64_bit_fields_as_32_bit
        del export_info['id']
        if args.new_export_path is not None:
            export_info['export_path'] = args.new_export_path
        if args.fs_path is not None:
            export_info['fs_path'] = args.fs_path
        if args.description is not None:
            export_info['description'] = args.description

        if args.restrictions:
            export_info['restrictions'] = parse_nfs_export_restrictions_file(
                args.restrictions)
        elif args.no_restrictions:
            export_info['restrictions'] = \
                [NFSExportRestriction.create_default()]
        else:
            export_info['restrictions'] = \
                [NFSExportRestriction(r) for r in export_info['restrictions']]

        print nfs.nfs_modify_export(conninfo, credentials, **export_info)

def add_user_mapping_from_args(entry, args, must_set=True):
    '''
    @p must_set indicates whether it is mandatory that a user mapping be
        set.  This would be False when modifying an entry that already has
        squashing enabled, in which case the anon user is already set and it is
        not necessary to change it.
    '''
    if must_set and not (args.anon_local or (args.anon_uid is not None)):
        raise ValueError(
            "Must specify an anonymous identity when enabling squashing.")
    if args.anon_local and (args.anon_gid is not None):
        raise ValueError(
            "Cannot specify both --anon-local and --anon-gid.")
    if args.anon_local:
        entry.map_to_user = {
            'id_type': 'LOCAL_USER',
            'id_value': util.check_unicode(args.anon_local, 'anon local')
        }
        if 'map_to_group' in entry.dictionary():
            del entry.map_to_group
    elif args.anon_uid is not None:
        if args.anon_gid is None:
            raise ValueError(
                "Must provide --anon-gid when --anon-uid is given.")
        entry.map_to_user = {
            'id_type': 'NFS_UID', 'id_value': str(args.anon_uid)}
        entry.map_to_group = {
            'id_type': 'NFS_GID', 'id_value': str(args.anon_gid)}

def modify_restrictions(conninfo, creds, old_export, etag, restrictions):
    return nfs.nfs_modify_export(
        conninfo,
        creds,
        old_export['id'],
        old_export['export_path'],
        old_export['fs_path'],
        old_export['description'],
        restrictions,
        present_64_bit_fields_as_32_bit=
            old_export['present_64_bit_fields_as_32_bit'],
        if_match=etag)

def do_add_entry(conninfo, creds, args):
    entry = NFSExportRestriction({
        'host_restrictions': args.hosts if args.hosts != ['*'] else [],
        'require_privileged_port': bool(args.secure),
        'read_only': bool(args.ro),
    })
    if args.root_squash:
        entry.user_mapping = 'NFS_MAP_ROOT'
        add_user_mapping_from_args(entry, args)
    elif args.all_squash:
        entry.user_mapping = 'NFS_MAP_ALL'
        add_user_mapping_from_args(entry, args)
    elif any([args.anon_local, args.anon_uid, args.anon_gid]):
        raise ValueError(
            "Anonymous identity cannot be given if squashing is disabled.")
    else:
        entry.user_mapping = 'NFS_MAP_NONE'

    old_export, etag = nfs.nfs_get_export(
        conninfo, creds, args.id, args.export_path)

    restrictions = [NFSExportRestriction(r) for r in old_export['restrictions']]
    # NB: list.insert inserts before, but the host entry list is 1-indexed, so
    # passing position to list.insert unchanged will insert after that position.
    restrictions.insert(
        len(restrictions) if args.insert_after is None else args.insert_after,
        entry)

    return modify_restrictions(conninfo, creds, old_export, etag, restrictions)

def validate_position(restrictions, position):
    if position < 1:
        raise ValueError("Position must be 1 or greater")
    if position > len(restrictions):
        raise ValueError("Position {} is greater than the maximum of {}".format(
            position, len(restrictions)))

def do_modify_entry(conninfo, creds, args):
    old_export, etag = nfs.nfs_get_export(
        conninfo, creds, args.id, args.export_path)
    validate_position(old_export['restrictions'], args.position)
    restrictions = [NFSExportRestriction(r) for r in old_export['restrictions']]

    entry = restrictions[args.position - 1]
    if args.hosts is not None:
        entry.host_restrictions = args.hosts if args.hosts != ["*"] else []
    if args.secure is not None:
        entry.require_privileged_port = args.secure
    if args.ro is not None:
        entry.read_only = args.ro
    if args.no_root_squash:
        entry.user_mapping = 'NFS_MAP_NONE'
        entry.map_to_user = None
        entry.map_to_group = None
    if args.root_squash:
        entry.user_mapping = 'NFS_MAP_ROOT'
        add_user_mapping_from_args(entry, args,
            must_set=not entry.dictionary().get('map_to_user', False))
    if args.all_squash:
        entry.user_mapping = 'NFS_MAP_ALL'
        add_user_mapping_from_args(entry, args,
            must_set=not entry.dictionary().get('map_to_user', False))
    if any([args.anon_local,
            args.anon_uid is not None, args.anon_gid is not None]):
        # Note that this must be ordered after setting the map mode above in
        # order for this check to be correct:
        if entry.user_mapping == 'NFS_MAP_NONE':
            raise ValueError(
                "Cannot set anonymous identity on a --no-root-squash export.")
        add_user_mapping_from_args(entry, args)

    return modify_restrictions(conninfo, creds, old_export, etag, restrictions)

def do_remove_entry(conninfo, creds, args):
    old_export, etag = nfs.nfs_get_export(
        conninfo, creds, args.id, args.export_path)
    validate_position(old_export['restrictions'], args.position)

    restrictions = [NFSExportRestriction(r)
        for i, r in enumerate(old_export['restrictions'])
        if i != (args.position - 1)]

    return modify_restrictions(conninfo, creds, old_export, etag, restrictions)

def add_common_export_args(subparser):
    '''
    Add options to parse the "secure", "ro", "no_root_sqush", "root_squash",
    "all_squash", "anon_local", "anon_uid", and "anon_gid" args.  In the case
    of "secure" and "ro", the value is None when unspecified, which allows
    modify_entry to determine whether those flags are to be changed.
    '''

    port = subparser.add_mutually_exclusive_group(required=False)
    # Set up flags to set "secure" either True or False, with the default
    # of None, which means insecure is the default but it is possible to
    # distinguish whether a value was explicitly specified.
    port.add_argument("--insecure",
        action='store_false', dest='secure', default=None,
        help="Hosts may use any source port to access this export. "
            "This is the default option.")
    port.add_argument("--secure", action='store_true', default=None,
        help="Require hosts to use privileged ports. Note that this will "
            "deny access to OSX clients that use default mount options.")
    rw = subparser.add_mutually_exclusive_group(required=False)
    rw.add_argument("--rw", action='store_false', dest='ro', default=None,
        help="Export allows both read and write access. "
            "This is the default option.")
    rw.add_argument("--ro", action='store_true', default=None,
        help="Export is read-only.")
    squash = subparser.add_mutually_exclusive_group(required=False)
    squash.add_argument("--no-root-squash", action='store_true',
        help="Don't map any users.  This is the default option.")
    squash.add_argument("--root-squash", action='store_true',
        help="Map access by root to the anonymous user.")
    squash.add_argument("--all-squash", action='store_true',
        help="Map all access to the anonymous user.")
    # If a squash option is provided, either --anon-local or both
    # --anon-uid and --anon-gid must be provided (unfortunately it
    # argparse can't validate this completely)
    anon = subparser.add_mutually_exclusive_group(required=False)
    anon.add_argument("--anon-local", type=str,
        help="The name of a local user to squash to.")
    anon.add_argument("--anon-uid", type=int,
        help="The NFS UID to squash to.")
    # Unfortunately argparse can't express "these two args must be provided
    # together or not at all, exclusive with this other arg."
    subparser.add_argument("--anon-gid", type=int,
        help="The NFS GID to squash to, when --anon-uid is given.")

class NFSModExportHostAccessCommand(qumulo.lib.opts.Subcommand):
    NAME = "nfs_mod_export_host_access"
    DESCRIPTION = "Modify the access hosts are granted to an export"

    @staticmethod
    def options(parser):
        export = parser.add_mutually_exclusive_group(required=True)
        export.add_argument("--id", type=str, default=None,
            help="ID of export to modify")
        export.add_argument("--export-path", type=str_decode, default=None,
            help="Path of export to modify")
        export.add_argument("--json", action='store_true',
            help="Print raw response JSON")

        subparsers = parser.add_subparsers()

        # Note that the arg names here are a bit odd because they've been
        # chosen to correspond with equivalent options in /etc/exports
        add_entry = subparsers.add_parser("add_entry",
            help="Add a new host access entry.")
        add_entry.set_defaults(function=do_add_entry)
        add_entry.add_argument("--hosts", "-o",
            type=str, required=False, nargs="+", default=["*"],
            help="Hosts to grant access to.  '*' matches all.  May be "
                "individual IP addresses, CIDR masks (e.g. 10.1.2.0/24), or "
                "ranges (e.g. 10.2.3.23-47, fd00::42:1fff-c000).  Export will "
                "match all by default.")
        add_entry.add_argument("--insert-after", "-a", type=int, default=None,
            help="Insert the new entry after the given position.  By default, "
                "the new entry will be added to the end of the host list.")
        add_common_export_args(add_entry)

        mod_entry = subparsers.add_parser(
            "modify_entry", help="Modify a host access entry.")
        mod_entry.set_defaults(function=do_modify_entry)
        mod_entry.add_argument("--position", "-p", required=True, type=int,
            help="The position of the entry to be removed.")
        mod_entry.add_argument("--hosts", "-o",
            type=str, required=False, nargs="+", default=None,
            help="Change the hosts granted access.  '*' matches all.  May be "
                "individual IP addresses, CIDR masks (e.g. 10.1.2.0/24), or "
                "ranges (e.g. 10.2.3.23-47, fd00::42:1fff-c000).")
        add_common_export_args(mod_entry)

        remove_entry = subparsers.add_parser(
            "remove_entry", help="Remove a host access entry.")
        remove_entry.set_defaults(function=do_remove_entry)
        remove_entry.add_argument("--position", "-p", required=True, type=int,
            help="The position of the entry to be removed.")

    @staticmethod
    def main(conninfo, credentials, args):
        response = args.function(conninfo, credentials, args)
        pretty_print_export(response[0], args.json)

class NFSDeleteExportCommand(qumulo.lib.opts.Subcommand):
    NAME = "nfs_delete_export"
    DESCRIPTION = "Delete an export"

    @staticmethod
    def options(parser):
        export = parser.add_mutually_exclusive_group(required=True)
        export.add_argument("--id", type=str, default=None,
            help="ID of export to delete")
        export.add_argument("--export-path", type=str_decode, default=None,
            help="Path of export to delete")

    @staticmethod
    def main(conninfo, credentials, args):
        nfs.nfs_delete_export(conninfo, credentials, args.id, args.export_path)
        print u"Export {} has been deleted.".format(
            args.id if args.id else u'"{}"'.format(args.export_path))
