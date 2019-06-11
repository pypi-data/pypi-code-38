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
import qumulo.lib.util
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

    nfs_export_restrictions = list()
    for r in restrictions['restrictions']:
        read_only = r.get('read_only', False)

        host_restrictions = r.get('host_restrictions', [])

        try:
            user_mapping = convert_nfs_user_mapping(
                                r.get('user_mapping', 'none'))

            restriction = NFSExportRestriction({
                                    'read_only': read_only,
                                    'host_restrictions': host_restrictions,
                                    'user_mapping': user_mapping
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
    def main(conninfo, credentials, _args):
        print nfs.nfs_list_exports(conninfo, credentials)

def str_decode(arg):
    '''
    Custom argparse type for decoding based on stdin-specific encoding. If stdin
    does not provide an encoding (e.g. is a pipe), then default to utf-8 for
    the sake of doing something relatively sane.
    '''
    return unicode(arg, sys.stdin.encoding or 'utf-8')

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

    @staticmethod
    def main(conninfo, credentials, args):
        print nfs.nfs_get_export(conninfo, credentials,
            args.id, args.export_path)

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
            type=qumulo.lib.util.bool_from_string,
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
            type=qumulo.lib.util.bool_from_string,
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
