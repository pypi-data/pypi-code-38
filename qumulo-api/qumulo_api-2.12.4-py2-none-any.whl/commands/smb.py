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

'''
Share commands
'''

import re
import sys

from qumulo.lib.acl_util import AceTranslator, AclEditor
import qumulo.lib.opts
from qumulo.lib.opts import str_decode
from qumulo.lib.util import bool_from_string, tabulate
import qumulo.rest.smb as smb

#     _    ____ _
#    / \  / ___| |
#   / _ \| |   | |
#  / ___ \ |___| |___
# /_/   \_\____|_____|_             _       _   _
# |  \/  | __ _ _ __ (_)_ __  _   _| | __ _| |_(_) ___  _ __
# | |\/| |/ _` | '_ \| | '_ \| | | | |/ _` | __| |/ _ \| '_ \
# | |  | | (_| | | | | | |_) | |_| | | (_| | |_| | (_) | | | |
# |_|  |_|\__,_|_| |_|_| .__/ \__,_|_|\__,_|\__|_|\___/|_| |_|
#                      |_|
# FIGLET: ACL Manipulation

NO_ACCESS = "NONE"
READ_ACCESS = "READ"
WRITE_ACCESS = "WRITE"
READ_WRITE_ACCESS = "READ|WRITE"
CHANGE_PERMISSIONS_ACCESS = "CHANGE_PERMISSIONS"
ALL_ACCESS = "ALL"
ALL_RIGHTS = (
    NO_ACCESS,
    READ_ACCESS,
    WRITE_ACCESS,
    CHANGE_PERMISSIONS_ACCESS,
    ALL_ACCESS
)

ALLOWED_TYPE = "ALLOWED"
DENIED_TYPE = "DENIED"

LOCAL_DOMAIN = "LOCAL"
WORLD_DOMAIN = "WORLD"
POSIX_USER_DOMAIN = "POSIX_USER"
POSIX_GROUP_DOMAIN = "POSIX_GROUP"
AD_DOMAIN = "ACTIVE_DIRECTORY"

EVERYONE_NAME = 'Everyone'
GUEST_NAME = 'Guest'

# A SID starts with S, followed by hyphen separated version, authority, and at
# least one sub-authority
SID_REGEXP = re.compile(r'S-[0-9]+-[0-9]+(?:-[0-9]+)+$')

VALID_DOMAIN_TYPES = ('local', 'world', 'ldap_user', 'ldap_group', 'ad')
VALID_TRUSTEE_TYPES = VALID_DOMAIN_TYPES + \
    ('name', 'sid', 'uid', 'gid', 'auth_id')

class ShareAceTranslator(AceTranslator):
    def _parse_rights(self, rights):
        api_rights = [r.upper().replace(' ', '_') for r in rights]
        assert(all(r in ALL_RIGHTS for r in api_rights))
        return api_rights

    def parse_rights(self, rights, ace):
        ace['rights'] = self._parse_rights(rights)

    def pretty_rights(self, ace):
        # Replace the _ in CHANGE_PERMISSIONS:
        rights = [r.replace("_", " ") for r in ace['rights']]
        rights = [r.capitalize() for r in rights]
        return ", ".join(rights)

    def ace_rights_equal(self, ace, rights):
        return set(ace['rights']) == set(self._parse_rights(rights))

    @property
    def has_flags(self):
        return False

    # Keeps pylint happy:
    def parse_flags(self, flags, ace):
        raise TypeError("SMB share aces do not have flags.")

    def pretty_flags(self, ace):
        raise TypeError("SMB share aces do not have flags.")

    def ace_flags_equal(self, ace, flags):
        raise TypeError("SMB share aces do not have flags.")

def pretty_share_list(shares):
    headers = ["ID", "Name", "Path", "Description"]
    rows = [[row["id"], row["share_name"], row["fs_path"], row["description"]]
            for row in shares]
    return tabulate(rows, headers)

#  _     _     _     ____  _
# | |   (_)___| |_  / ___|| |__   __ _ _ __ ___  ___
# | |   | / __| __| \___ \| '_ \ / _` | '__/ _ \/ __|
# | |___| \__ \ |_   ___) | | | | (_| | | |  __/\__ \
# |_____|_|___/\__| |____/|_| |_|\__,_|_|  \___||___/
# FIGLET: List Shares

class SMBListSharesCommand(qumulo.lib.opts.Subcommand):
    NAME = "smb_list_shares"
    DESCRIPTION = "List all SMB shares"

    @staticmethod
    def options(parser):
        parser.add_argument("--json", action="store_true",
            help="Print JSON representation of shares.")

    @staticmethod
    def main(conninfo, credentials, args):
        res = smb.smb_list_shares(conninfo, credentials)
        if args.json:
            print res
        else:
            print pretty_share_list(res.data)

def _print_share(response, json, outfile):
    if json:
        outfile.write("{}\n".format(response))
    else:
        body, _etag = response
        outfile.write(
            u"ID: {id}\n"
            u"Name: {share_name}\n"
            u"Path: {fs_path}\n"
            u"Description: {description}\n"
            u"Access Based Enumeration: "
                u"{access_based_enumeration_enabled}\n"
            u"Default File Create Mode: {default_file_create_mode}\n"
            u"Default Directory Create Mode: "
                u"{default_directory_create_mode}\n"
            .format(**body))
        outfile.write("\n")
        outfile.write("Permissions:\n{}\n".format(
            AclEditor(ShareAceTranslator(), body['permissions']).pretty_str()))

class SMBListShareCommand(qumulo.lib.opts.Subcommand):
    NAME = "smb_list_share"
    DESCRIPTION = "List a share"

    @staticmethod
    def options(parser):
        share = parser.add_mutually_exclusive_group(required=True)
        share.add_argument("--id", type=int, default=None,
            help="ID of share to list")
        share.add_argument("--name", type=str_decode, default=None,
            help="Name of share to list")

        parser.add_argument("--json", action='store_true', default=False,
            help="Print the raw JSON response.")

    @staticmethod
    def main(conninfo, credentials, args):
        _print_share(
            smb.smb_list_share(conninfo, credentials, args.id, args.name),
            args.json, sys.stdout)

#     _       _     _   ____  _
#    / \   __| | __| | / ___|| |__   __ _ _ __ ___
#   / _ \ / _` |/ _` | \___ \| '_ \ / _` | '__/ _ \
#  / ___ \ (_| | (_| |  ___) | | | | (_| | | |  __/
# /_/   \_\__,_|\__,_| |____/|_| |_|\__,_|_|  \___|
# FIGLET: Add Share

def _add_initial_acl_args(parser):
    # Permissions options:
    exclusive_perms = parser.add_mutually_exclusive_group()
    exclusive_perms.add_argument("--no-access", action='store_true',
        default=False,
        help="Grant no access.")
    exclusive_perms.add_argument("--read-only", action='store_true',
        default=False,
        help="Grant everyone except guest read-only access.")
    exclusive_perms.add_argument("--all-access", action='store_true',
        default=False,
        help="Grant everyone except guest full access.")

    # These are all exclusive with read-only or no-access, but not with
    # all-access or each other, which argparse can't express:
    parser.add_argument("--grant-read-access", type=str_decode, nargs='+',
        metavar='TRUSTEE',
        help="Grant read access to these trustees.  e.g. Everyone, "
             "uid:1000, gid:1001, sid:S-1-5-2-3-4, or auth_id:500")
    parser.add_argument("--grant-read-write-access",
        type=str_decode, nargs='+', metavar="TRUSTEE",
        help="Grant read-write access to these trustees.")
    parser.add_argument("--grant-all-access", type=str_decode, nargs='+',
        metavar="TRUSTEE",
        help="Grant all access to these trustees.")
    parser.add_argument("--deny-access", type=str_decode, nargs='+',
        metavar="TRUSTEE",
        help="Deny all access to these trustees.")

def _create_new_acl(args):
    have_grants = any([args.all_access, args.grant_read_access,
        args.grant_read_write_access, args.grant_all_access])
    if args.no_access and have_grants:
        raise ValueError("Cannot specify --no-access and grant other access.")
    if args.read_only and have_grants:
        raise ValueError("Cannot specify --read-only and grant other access.")
    if not any([args.no_access, args.read_only, args.deny_access, have_grants]):
        raise ValueError("Must specify initial permissions (--no-access, "
            "--read-only, --all-access, --grant-read-access, etc.)")

    acl = AclEditor(ShareAceTranslator())

    # Note that order shouldn't matter, the AclEditor should always put
    # these ACEs at the beginning, so they will override any grants
    if args.deny_access:
        acl.deny(args.deny_access, [ALL_ACCESS])

    if args.read_only:
        acl.grant([EVERYONE_NAME], [READ_ACCESS])
    if args.all_access:
        acl.grant([EVERYONE_NAME], [ALL_ACCESS])
    if args.grant_read_access:
        acl.grant(args.grant_read_access, [READ_ACCESS])
    if args.grant_read_write_access:
        acl.grant(args.grant_read_write_access, [READ_ACCESS, WRITE_ACCESS])
    if args.grant_all_access:
        acl.grant(args.grant_all_access, [ALL_ACCESS])

    return acl.acl

class SMBAddShareCommand(qumulo.lib.opts.Subcommand):
    NAME = "smb_add_share"
    DESCRIPTION = "Add a new SMB share"

    @staticmethod
    def options(parser):
        parser.add_argument("--name",
            type=str_decode, default=None, required=True,
            help="Name of share")
        parser.add_argument("--fs-path",
            type=str_decode, default=None, required=True,
            help="File system path")
        parser.add_argument("--description", type=str_decode, default='',
            help="Description of this share")
        parser.add_argument("--access-based-enumeration-enabled",
            type=bool, default=False,
            help="Enable Access-based Enumeration on this share")
        parser.add_argument("--create-fs-path", action="store_true",
            help="Creates the specified file system path if it does not exist")
        parser.add_argument("--default-file-create-mode",
            type=str_decode, default=None,
            help="Default POSIX file create mode bits on this SMB share \
                (octal, 0644 will be used if not provided)")
        parser.add_argument("--default-directory-create-mode",
            type=str_decode, default=None,
            help="Default POSIX directory create mode bits on this SMB share \
                (octal, 0755 will be used if not provided)")
        parser.add_argument("--bytes-per-sector",
            type=int, default=None,
            help='SMB bytes per sector reported to clients. Only 4096 '
                 '(default) and 512 are allowed.')
        parser.add_argument("--json", action='store_true', default=False,
            help="Print the raw JSON response.")

        _add_initial_acl_args(parser)

    @staticmethod
    def main(conninfo, credentials, args, outfile=sys.stdout, smb_mod=smb):
        acl = _create_new_acl(args)

        result = smb_mod.smb_add_share(conninfo, credentials,
            args.name,
            args.fs_path,
            args.description,
            permissions=acl,
            allow_fs_path_create=args.create_fs_path,
            access_based_enumeration_enabled=
                args.access_based_enumeration_enabled,
            default_file_create_mode=
                args.default_file_create_mode,
            default_directory_create_mode=
                args.default_directory_create_mode,
            bytes_per_sector=args.bytes_per_sector)

        _print_share(result, args.json, outfile)

#  ____       _      _         ____  _
# |  _ \  ___| | ___| |_ ___  / ___|| |__   __ _ _ __ ___
# | | | |/ _ \ |/ _ \ __/ _ \ \___ \| '_ \ / _` | '__/ _ \
# | |_| |  __/ |  __/ ||  __/  ___) | | | | (_| | | |  __/
# |____/ \___|_|\___|\__\___| |____/|_| |_|\__,_|_|  \___|
# FIGLET: Delete Share

class SMBDeleteShareCommand(qumulo.lib.opts.Subcommand):
    NAME = "smb_delete_share"
    DESCRIPTION = "Delete a share"

    @staticmethod
    def options(parser):
        share = parser.add_mutually_exclusive_group(required=True)
        share.add_argument("--id", type=int, default=None,
            help="ID of share to delete")
        share.add_argument("--name", type=str_decode, default=None,
            help="Name of share to delete")

    @staticmethod
    def main(conninfo, credentials, args, outfile=sys.stdout, smb_mod=smb):
        smb_mod.smb_delete_share(conninfo, credentials, args.id, args.name)
        outfile.write(u"Share {} has been deleted.\n".format(
            args.id if args.id else u'"{}"'.format(args.name)))

#  __  __           _ _  __         ____  _
# |  \/  | ___   __| (_)/ _|_   _  / ___|| |__   __ _ _ __ ___
# | |\/| |/ _ \ / _` | | |_| | | | \___ \| '_ \ / _` | '__/ _ \
# | |  | | (_) | (_| | |  _| |_| |  ___) | | | | (_| | | |  __/
# |_|  |_|\___/ \__,_|_|_|  \__, | |____/|_| |_|\__,_|_|  \___|
#                           |___/
# FIGLET: Modify Share

class SMBModShareCommand(qumulo.lib.opts.Subcommand):
    NAME = "smb_mod_share"
    DESCRIPTION = "Modify a share"

    @staticmethod
    def options(parser):
        share = parser.add_mutually_exclusive_group(required=True)
        share.add_argument("--id", type=int, default=None,
            help="ID of share to modify")
        share.add_argument("--name", type=str_decode, default=None,
            help="Name of share to modify")

        parser.add_argument("--new-name", default=None,
            help="Change SMB share name")
        parser.add_argument("--fs-path", type=str_decode, default=None,
            help="Change file system path")
        parser.add_argument("--description", type=str_decode, default=None,
            help="Change description of this share")
        parser.add_argument("--access-based-enumeration-enabled",
            type=str_decode, default=None,
            help="Change if Access-based Enumeration is enabled on this share")
        parser.add_argument("--create-fs-path", action="store_true",
            help="Creates the specified file system path if it does not exist")
        parser.add_argument("--default-file-create-mode",
            type=str_decode, default=None,
            help="Change default POSIX file create mode bits (octal) on this \
                SMB share")
        parser.add_argument("--default-directory-create-mode",
            type=str_decode, default=None,
            help="Change default POSIX directory create mode bits (octal) on \
                this SMB share")
        parser.add_argument("--bytes-per-sector",
            type=int, default=None,
            help='SMB bytes per sector reported to clients. Only 4096 '
                 '(default) and 512 are allowed.')
        parser.add_argument("--json", action='store_true', default=False,
            help="Print the raw JSON response.")

    @staticmethod
    def main(conninfo, credentials, args, outfile=sys.stdout, smb_mod=smb):
        # N.B. Strictly one of args.id and args.name is allowed to be None
        share_info = { 'id_': args.id, 'old_name': args.name }

        if args.create_fs_path is True:
            share_info['allow_fs_path_create'] = True

        if args.new_name is not None:
            share_info['share_name'] = args.new_name
        if args.fs_path is not None:
            share_info['fs_path'] = args.fs_path
        if args.description is not None:
            share_info['description'] = args.description
        if args.access_based_enumeration_enabled is not None:
            share_info['access_based_enumeration_enabled'] = bool_from_string(
                args.access_based_enumeration_enabled)
        if args.default_file_create_mode is not None:
            share_info['default_file_create_mode'] = \
                args.default_file_create_mode
        if args.default_directory_create_mode is not None:
            share_info['default_directory_create_mode'] = \
                args.default_directory_create_mode
        if args.bytes_per_sector is not None:
            share_info['bytes_per_sector'] = str(args.bytes_per_sector)

        _print_share(
            smb_mod.smb_modify_share(conninfo, credentials, **share_info),
            args.json, outfile)

#  __  __           _ _  __
# |  \/  | ___   __| (_)/ _|_   _
# | |\/| |/ _ \ / _` | | |_| | | |
# | |  | | (_) | (_| | |  _| |_| |
# |_|  |_|\___/ \__,_|_|_|  \__, |
#  ___                      |___/     _
# |  _ \ ___ _ __ _ __ ___ (_)___ ___(_) ___  _ __  ___
# | |_) / _ \ '__| '_ ` _ \| / __/ __| |/ _ \| '_ \/ __|
# |  __/  __/ |  | | | | | | \__ \__ \ | (_) | | | \__ \
# |_|   \___|_|  |_| |_| |_|_|___/___/_|\___/|_| |_|___/
# FIGLET: Modify Permissions

TYPE_CHOICES = [t.capitalize() for t in [ALLOWED_TYPE, DENIED_TYPE]]
RIGHT_CHOICES = [t.replace('_', ' ').capitalize() for t in ALL_RIGHTS]

def _put_new_acl(smb_mod, conninfo, creds, share, new_acl, etag, print_json):
    result = smb_mod.smb_modify_share(conninfo, creds,
        id_=share['id'],
        permissions=new_acl,
        if_match=etag)

    if print_json:
        return str(result)
    else:
        body, etag = result
        return 'New permissions:\n{}'.format(
            AclEditor(ShareAceTranslator(), body['permissions']).pretty_str())

def _get_share(smb_mod, conninfo, creds, _id, name):
    return smb_mod.smb_list_share(conninfo, creds, _id, name)

def do_add_entry(smb_mod, conninfo, creds, args):
    share, etag = _get_share(smb_mod, conninfo, creds, args.id, args.name)

    # Modify:
    translator = ShareAceTranslator()
    acl = AclEditor(translator, share['permissions'])
    ace_type = translator.parse_type_enum_value(args.type)
    if ace_type == ALLOWED_TYPE:
        acl.grant([args.trustee], args.rights)
    else:
        assert ace_type == DENIED_TYPE
        acl.deny([args.trustee], args.rights)

    if args.dry_run:
        return 'New permissions would be:\n{}'.format(acl.pretty_str())

    return _put_new_acl(
        smb_mod, conninfo, creds, share, acl.acl, etag, args.json)

def do_remove_entry(smb_mod, conninfo, creds, args):
    share, etag = _get_share(smb_mod, conninfo, creds, args.id, args.name)

    # Remove:
    acl = AclEditor(ShareAceTranslator(), share['permissions'])
    acl.remove(position=args.position,
        trustee=args.trustee,
        ace_type=args.type,
        rights=args.rights,
        allow_multiple=args.all_matching)

    if args.dry_run:
        return 'New permissions would be:\n{}'.format(acl.pretty_str())

    return _put_new_acl(
        smb_mod, conninfo, creds, share, acl.acl, etag, args.json)

def do_modify_entry(smb_mod, conninfo, creds, args):
    share, etag = _get_share(smb_mod, conninfo, creds, args.id, args.name)

    acl = AclEditor(ShareAceTranslator(), share['permissions'])
    acl.modify(args.position,
        args.old_trustee, args.old_type, args.old_rights, None,
        args.new_trustee, args.new_type, args.new_rights, None,
        args.all_matching)

    if args.dry_run:
        return 'New permissions would be:\n{}'.format(acl.pretty_str())

    return _put_new_acl(
        smb_mod, conninfo, creds, share, acl.acl, etag, args.json)

def do_replace(smb_mod, conninfo, creds, args):
    share, etag = _get_share(smb_mod, conninfo, creds, args.id, args.name)
    acl = _create_new_acl(args)

    if args.dry_run:
        return 'New permissions would be:\n{}'.format(
            AclEditor(ShareAceTranslator(), acl).pretty_str())

    return _put_new_acl(
        smb_mod, conninfo, creds, share, acl, etag, args.json)

# This is separate from smb_mode_share because argparse doesn't allow
# sub-commands to be optional.
class SMBModShareAclCommand(qumulo.lib.opts.Subcommand):
    NAME = "smb_mod_share_permissions"
    DESCRIPTION = "Modify a share's permissions"

    @staticmethod
    def options(parser):
        share = parser.add_mutually_exclusive_group(required=True)
        share.add_argument("--id", type=int, default=None,
            help="ID of share to modify")
        share.add_argument("--name", type=str_decode, default=None,
            help="Name of share to modify")

        parser.add_argument("--json", action='store_true', default=False,
            help="Print the raw JSON response.")

        subparsers = parser.add_subparsers()

        add_entry = subparsers.add_parser("add_entry",
            help="Add an entry to the share's permissions.")
        add_entry.set_defaults(function=do_add_entry)
        add_entry.add_argument("-t", "--trustee",
            type=str_decode, required=True,
            help="The trustee to add.  e.g. Everyone, uid:1000, gid:1001, "
                 "sid:S-1-5-2-3-4, or auth_id:500")
        add_entry.add_argument("-y", "--type", type=str_decode, required=True,
            choices=TYPE_CHOICES,
            help="Whether the trustee should be allowed or denied the "
                "given rights")
        add_entry.add_argument("-r", "--rights", type=str_decode, nargs="+",
            required=True, metavar='RIGHT',
            choices=RIGHT_CHOICES,
            help="The rights that should be allowed or denied.  Choices: "
                 + (", ".join(RIGHT_CHOICES)))
        add_entry.add_argument("-d", "--dry-run", action='store_true',
            default=False,
            help="Do nothing; display what the result of the change would be.")

        remove_entry = subparsers.add_parser("remove_entry",
            help="Remove an entry from the share's permissions")
        remove_entry.set_defaults(function=do_remove_entry)
        remove_entry.add_argument("-p", "--position", type=int,
            help="The position of the entry to remove.")
        remove_entry.add_argument("-t", "--trustee", type=str_decode,
            help="Remove an entry with this trustee.  e.g. Everyone, "
                 "uid:1000, gid:1001, sid:S-1-5-2-3-4, or auth_id:500")
        remove_entry.add_argument("-y", "--type", type=str_decode,
            choices=TYPE_CHOICES, help="Remove an entry of this type")
        remove_entry.add_argument("-r", "--rights", type=str_decode, nargs="+",
             metavar='RIGHT',
            choices=RIGHT_CHOICES,
            help="Remove an entry with these rights.  Choices: "
                 + (", ".join(RIGHT_CHOICES)))
        remove_entry.add_argument("-a", "--all-matching", action='store_true',
            default=False, help="If multiple entries match the "
                "arguments, remove all of them")
        remove_entry.add_argument("-d", "--dry-run", action='store_true',
            default=False,
            help="Do nothing; display what the result of the change would be.")

        modify_entry = subparsers.add_parser("modify_entry",
            help="Modify an existing permission entry in place")
        modify_entry.set_defaults(function=do_modify_entry)
        modify_entry.add_argument("-p", "--position", type=int,
            help="The position of the entry to modify.")
        modify_entry.add_argument("--old-trustee", type=str_decode,
            help="Modify an entry with this trustee.  e.g. Everyone, "
                 "uid:1000, gid:1001, sid:S-1-5-2-3-4, or auth_id:500")
        modify_entry.add_argument("--old-type", type=str_decode,
            choices=TYPE_CHOICES, help="Modify an entry of this type")
        modify_entry.add_argument("--old-rights", type=str_decode, nargs="+",
             metavar='RIGHT',
            choices=RIGHT_CHOICES,
            help="Modify an entry with these rights.  Choices: "
                 + (", ".join(RIGHT_CHOICES)))
        modify_entry.add_argument("--new-trustee", type=str_decode,
            help="Set the entry to have this trustee.  e.g. Everyone, "
                 "uid:1000, gid:1001, sid:S-1-5-2-3-4, or auth_id:500")
        modify_entry.add_argument("--new-type", type=str_decode,
            choices=TYPE_CHOICES, help="Set the type of the entry.")
        modify_entry.add_argument("--new-rights", type=str_decode, nargs="+",
             metavar='RIGHT',
            choices=RIGHT_CHOICES,
            help="Set the rights of the entry.  Choices: "
                 + (", ".join(RIGHT_CHOICES)))
        modify_entry.add_argument("-a", "--all-matching", action='store_true',
            default=False, help="If multiple entries match the arguments, "
                "modify all of them")
        modify_entry.add_argument(
            "-d", "--dry-run", action='store_true', default=False,
            help="Do nothing; display what the result of the change would be.")

        replace = subparsers.add_parser("replace",
            help="Replace any existing share permissions with new permissions. "
                 "If no new permissions are specified, all access will be "
                 "denied.")
        replace.add_argument(
            "-d", "--dry-run", action='store_true', default=False,
            help="Do nothing; display what the result of the change would be.")
        _add_initial_acl_args(replace)
        replace.set_defaults(function=do_replace)

    @staticmethod
    def main(conninfo, credentials, args, outfile=sys.stdout, smb_mod=smb):
        outfile.write('{}\n'.format(
            args.function(smb_mod, conninfo, credentials, args)))
