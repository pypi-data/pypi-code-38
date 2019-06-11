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

import argparse
import collections
import json
import os.path
import pipes
import re
import sys
import textwrap

import qumulo.lib.auth
import qumulo.lib.opts
import qumulo.lib.request as request
import qumulo.lib.util as util
import qumulo.rest.fs as fs

from qumulo.lib.acl_util import AceTranslator, AclEditor
from qumulo.lib.identity_util import Identity
from qumulo.lib.opts import str_decode

AGG_ORDERING_CHOICES = [
    "total_blocks",
    "total_datablocks",
    "total_named_stream_datablocks",
    "total_metablocks",
    "total_files",
    "total_directories",
    "total_symlinks",
    "total_other",
    "total_named_streams"]

LOCK_RELEASE_FORCE_MSG = "Manually releasing locks may cause data corruption, "\
                         "do you want to proceed?"

def all_elements_none(iterable):
    for element in iterable:
        if element is not None:
            return False
    return True

class GetStatsCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_get_stats"
    DESCRIPTION = "Get file system statistics"

    @staticmethod
    def main(conninfo, credentials, _args):
        print fs.read_fs_stats(conninfo, credentials)

class GetFileAttrCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_file_get_attr"
    DESCRIPTION = "Get file attributes"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to file", type=str)
        group.add_argument("--id", help="File ID", type=str)
        parser.add_argument("--snapshot", help="Snapshot ID to read from",
            type=int)
        # TODO ADS: Remove suppress for actual release
        parser.add_argument("--stream-id", help=argparse.SUPPRESS)

    @staticmethod
    def main(conninfo, credentials, args):
        print fs.get_file_attr(
            conninfo,
            credentials,
            id_=args.id,
            path=args.path,
            snapshot=args.snapshot,
            stream_id=args.stream_id)

class SetFileAttrCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_file_set_attr"
    DESCRIPTION = "Set file attributes"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to file", type=str)
        group.add_argument("--id", help="File ID", type=str)

        parser.add_argument("--mode", type=str,
                            help="Posix-style file mode (octal)")
        parser.add_argument("--size", help="File size", type=str)
        parser.add_argument("--creation-time", type=str,
                            help='File creation time (as RFC 3339 string)')
        parser.add_argument("--modification-time", type=str,
                            help='File modification time (as RFC 3339 string)')
        parser.add_argument("--change-time", type=str,
                            help='File change time (as RFC 3339 string)')
        # TODO ADS: Remove suppress for actual release
        parser.add_argument("--stream-id", help=argparse.SUPPRESS)

        owner_group = parser.add_mutually_exclusive_group()
        owner_group.add_argument("--owner",
            help="File owner as auth_id", type=str)
        owner_group.add_argument("--owner-local",
            help="File owner as local user name", type=fs.LocalUser)
        owner_group.add_argument("--owner-sid",
            help="File owner as SID", type=fs.SMBSID)
        owner_group.add_argument("--owner-uid",
            help="File owner as NFS UID", type=fs.NFSUID)

        group_group = parser.add_mutually_exclusive_group()
        group_group.add_argument("--group",
            help="File group as auth_id", type=str)
        group_group.add_argument("--group-local",
            help="File group as local group name", type=fs.LocalGroup)
        group_group.add_argument("--group-sid",
            help="File group as SID", type=fs.SMBSID)
        group_group.add_argument("--group-gid",
            help="File group as NFS GID", type=fs.NFSGID)

    @staticmethod
    def main(conninfo, credentials, args):
        owner = args.owner or \
                args.owner_local or args.owner_sid or args.owner_uid
        group = args.group or \
                args.group_local or args.group_sid or args.group_gid

        if all_elements_none([args.mode, owner, group, args.size,
                              args.creation_time, args.modification_time,
                              args.change_time]):
            raise ValueError("Must specify at least one option to change.")

        print fs.set_file_attr(
            conninfo,
            credentials,
            args.mode,
            owner,
            group,
            args.size,
            args.creation_time,
            args.modification_time,
            args.change_time,
            id_=args.id,
            path=args.path,
            stream_id=args.stream_id)

EXTENDED_FILE_ATTRS = (
    'archive',
    'compressed',
    'hidden',
    'not_content_indexed',
    'read_only',
    'system',
    'temporary',
)

class SetSmbFileAttrsCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_file_set_smb_attrs"
    DESCRIPTION = "Change SMB extended attributes on the file"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="File path")
        group.add_argument("--id", help="File id", type=int)

        for attr in EXTENDED_FILE_ATTRS:
            opt_string = '--' + attr.replace('_', '-')
            help_str = (
                'Set {} to a boolean-like value '
                '(e.g. true, false, yes, no, 1, 0).'.format(attr.upper()))
            parser.add_argument(
                opt_string,
                dest=attr,
                metavar='BOOL',
                type=util.bool_from_string,
                help=help_str)

    @staticmethod
    def main(conninfo, credentials, args):
        new_extended_attrs = {}
        etag = None
        if any(getattr(args, attr) is None for attr in EXTENDED_FILE_ATTRS):
            all_attrs, etag = fs.get_file_attr(
                conninfo, credentials, args.id, args.path)
            new_extended_attrs = all_attrs['extended_attributes']

        for attr in EXTENDED_FILE_ATTRS:
            attr_val = getattr(args, attr)
            if attr_val is not None:
                new_extended_attrs[attr] = attr_val

        print fs.set_file_attr(
            conninfo,
            credentials,
            id_=args.id,
            path=args.path,
            extended_attrs=new_extended_attrs,
            if_match=etag)

NFS_GID_TRUSTEE_TYPE = 'NFS_GID'
NFS_UID_TRUSTEE_TYPE = 'NFS_UID'
LOCAL_USER_TRUSTEE_TYPE = 'LOCAL_USER'
LOCAL_GROUP_TRUSTEE_TYPE = 'LOCAL_GROUP'
SID_TRUSTEE_TYPE = 'SMB_SID'
INTERNAL_TRUSTEE_TYPE = 'INTERNAL'

EVERYONE_NAME = 'Everyone'
EVERYONE_AUTH_ID = str(0x200000000) # WORLD_DOMAIN_ID << 32
FILE_OWNER_NAME = 'File Owner'
FILE_GROUP_OWNER_NAME = 'File Group Owner'

# These are the values actually produced / accepted by the API
ALL_RIGHTS = {
    'READ',
    'READ_EA',
    'READ_ATTR',
    'READ_ACL',
    'WRITE_EA',
    'WRITE_ATTR',
    'WRITE_ACL',
    'CHANGE_OWNER',
    'WRITE_GROUP',
    'DELETE',
    'EXECUTE',
    'MODIFY',
    'EXTEND',
    'ADD_FILE',
    'ADD_SUBDIR',
    'DELETE_CHILD',
    'SYNCHRONIZE',
}

# This maps the enum values used in the API to human-friendly output.
# A few of the right enum values have confusing names ("Modify" in particular
# gets confused with the Windows preset, and "Read" tends to suggest a much
# broader set of rights), so a simple text transform isn't great here:
API_RIGHTS_TO_CLI = {
    'READ': 'Read contents',
    'READ_EA': 'Read EA',
    'READ_ATTR': 'Read attr',
    'READ_ACL': 'Read ACL',
    'WRITE_EA': 'Write EA',
    'WRITE_ATTR': 'Write attr',
    'WRITE_ACL': 'Write ACL',
    'CHANGE_OWNER': 'Change owner',
    'WRITE_GROUP': 'Write group',
    'DELETE': 'Delete',
    'EXECUTE': 'Execute/Traverse',
    'MODIFY': 'Write data',
    'EXTEND': 'Extend file',
    'ADD_FILE': 'Add file',
    'ADD_SUBDIR': 'Add subdir',
    'DELETE_CHILD': 'Delete child',
    'SYNCHRONIZE': 'Synchronize'
}
# The reverse mapping, for interpreting input:
CLI_RIGHTS_TO_API = {v: k for k, v in API_RIGHTS_TO_CLI.items()}
# Plus some convenient aliases:
CLI_RIGHTS_TO_API.update({
    'Execute': 'EXECUTE',
    'Traverse': 'EXECUTE',
})

# These correspond to posix bits, and also qfsd default ACLs:
POSIX_READ_RIGHTS = frozenset(['READ', 'READ_EA', 'READ_ATTR', 'READ_ACL'])
POSIX_WRITE_FILE_RIGHTS = frozenset(
    ['WRITE_ATTR', 'WRITE_EA', 'EXTEND', 'MODIFY'])
# POSIX_WRITE_DIR_RIGHTS is not included because trying to distinguish it from
# WINDOWS_MODIFY_DIR_RIGHTS makes for confusion.  DELETE_CHILD will just have
# to be input/output as a separate item.

# This corresponds to the Windows preset:
WINDOWS_TAKE_OWNERSHIP_RIGHTS = frozenset(['CHANGE_OWNER', 'WRITE_GROUP'])
# When applied to a directory, this set of rights has the same meaning as
# the Windows "Modify" preset.  Unfortunately, this set of rights does not
# have the same meaning as "Modify" when applied to a file.  Since those
# sets of qfsd rights are disjoint, there's no reasonably simple way of
# providing an exact equivalent to the "Modify" preset.
WINDOWS_MODIFY_DIR_RIGHTS = frozenset(
    ['WRITE_ATTR', 'WRITE_EA', 'ADD_FILE', 'ADD_SUBDIR'])

# This maps user input to sets of rights that are commonly granted together:
SHORTHAND_RIGHTS_TO_API = {
    'All': frozenset(ALL_RIGHTS),
    'Read': POSIX_READ_RIGHTS,
    'Write file': POSIX_WRITE_FILE_RIGHTS,
    'Take ownership': WINDOWS_TAKE_OWNERSHIP_RIGHTS,
    'Write directory': WINDOWS_MODIFY_DIR_RIGHTS,
}

OBJECT_INHERIT_FLAG = 'OBJECT_INHERIT'
CONTAINER_INHERIT_FLAG = 'CONTAINER_INHERIT'
NO_PROPAGATE_INHERIT_FLAG = 'NO_PROPAGATE_INHERIT'
INHERIT_ONLY_FLAG = 'INHERIT_ONLY'
INHERITED_FLAG = 'INHERITED'

ALL_FLAGS = {
    OBJECT_INHERIT_FLAG,
    CONTAINER_INHERIT_FLAG,
    NO_PROPAGATE_INHERIT_FLAG,
    INHERIT_ONLY_FLAG,
    INHERITED_FLAG,
}

# A SID starts with S, followed by hyphen separated version, authority, and at
# least one sub-authority
SID_REGEXP = re.compile(r'S-[0-9]+-[0-9]+(?:-[0-9]+)+$')

def get_pretty_rights_string(rights, hide_synchronize=False):
    if rights == ALL_RIGHTS:
        # No need to print any other rights if we have ALL_RIGHTS
        return 'All'

    # Note that some of these overlap partially; printing both of the
    # overlapping sets is the desired outcome.
    res = []
    consumed_rights = set()
    for shorthand, values in SHORTHAND_RIGHTS_TO_API.items():
        if rights.issuperset(values):
            res.append(shorthand)
            consumed_rights.update(values)

    # The synchronize right is mostly useless, except that granting it is
    # basically mandatory for successful SMB access.  Hide it from output on
    # allow ACEs because it's ugly and confusing.  Don't hide it for deny
    # because it probably shouldn't be there and is probably breaking things.
    # It's not included in the presets for the same reason - because it
    # shouldn't be included when deny ACEs are created with those presets.
    # (Windows permissions dialog is similarly insane)
    if hide_synchronize and len(rights) > 1:
        consumed_rights.add('SYNCHRONIZE')

    # Add any individual values that didn't get covered by a shorthand:
    for right in rights:
        if right not in consumed_rights:
            res.append(API_RIGHTS_TO_CLI[right])

    return ", ".join(sorted(res))

def get_pretty_flags(flags):
    pretty_flags = [r.replace("_", " ") for r in flags]
    pretty_flags = [r.capitalize() for r in pretty_flags]
    return ", ".join(pretty_flags)

# list the shorthand rights ahead of the specific rights
RIGHT_CHOICES = \
    sorted(list(SHORTHAND_RIGHTS_TO_API.keys())) + \
    sorted(CLI_RIGHTS_TO_API.keys())

def normalize_rights_args(rights):
    '''
    Takes a list of right arguments (which are any strings) and maps them
    to matching keys in CLI_RIGHTS_TO_API or SHORTHAND_RIGHTS_TO_API,
    normalizing for comma separation, missing arg whitespace escaping, and case.
    In addition to being broadly tolerant of minor "errors", this means that
    it's possible to copy+paste rights from a pretty-printed ACL directly in to
    a command line without quoting, escaping, or removing commas.
    '''
    # Tokenize to lowercase words, by commas and whitespace:
    lower_rights = [r.lower() for r in rights]
    tokens = ' '.join(lower_rights).replace(',', ' ').replace('_', ' ').split()

    # Greedily put the tokens back together into a sequence of valid choices:
    lower_choices = {c.lower(): c for c in RIGHT_CHOICES}
    accumulator = []
    res = []
    for i, tok in enumerate(tokens):
        accumulator.append(tok)
        joined = ' '.join(accumulator)
        # Crude look-ahead to see if we can build a longer right if we add the
        # next token, which resolves the ambiguity between e.g.
        # ["read", "execute"] and ["read", "contents"].
        if (i + 1 < len(tokens)):
            if joined + ' ' + tokens[i+1] in lower_choices:
                continue
        if joined in lower_choices:
            res.append(lower_choices[joined])
            accumulator = []

    if accumulator:
        raise ValueError(
            'Bad rights, error near "{}": {}'.format(
                accumulator[0],
                ' '.join([repr(r) for r in rights])))

    return res

class FsAceTranslator(AceTranslator):
    def parse_rights_enum_values(self, rights):
        res = set()
        # Expand any shorthand rights, map and validate the rest as enum values
        for arg_right in rights:
            if arg_right in SHORTHAND_RIGHTS_TO_API:
                res.update(SHORTHAND_RIGHTS_TO_API[arg_right])
            else:
                api_right = CLI_RIGHTS_TO_API[arg_right]
                assert api_right in ALL_RIGHTS
                res.add(api_right)
        return res

    def parse_rights(self, rights, ace):
        rights = normalize_rights_args(rights)
        rights = self.parse_rights_enum_values(rights)
        # Although the synchronize right means nothing to Qumulo, SMB clients
        # will often ask for it.  If it's not granted, they will be denied
        # access, rendering the rest of the granted rights useless.  So,
        # whenever rights are granted, implicitly also grant the synchronize
        # right.  This can't be done unconditionally, because doing this for a
        # deny ACE would effectively deny access over SMB. (Windows permissions
        # dialog has the same insanity)
        if ace['type'] == ALLOWED_TYPE:
            rights.add('SYNCHRONIZE')
        ace['rights'] = list(sorted(rights))

    def pretty_rights(self, ace):
        # Translate as many of the values to shorthand as possible.  Note that
        # there is some overlap between some of the shorthand.  Rights lists
        # that include multiple overlapping shorthands should produce all of
        # those shorthands (i.e. the common rights may be represented multiple
        # times)
        rights = set(ace['rights'])
        return get_pretty_rights_string(
            rights, hide_synchronize=(ace.get('type')==ALLOWED_TYPE))

    def ace_rights_equal(self, ace, rights):
        return set(ace['rights']) == self.parse_rights_enum_values(rights)

    @property
    def has_flags(self):
        return True

    def parse_flags_enum_values(self, flags):
        if not flags:
            return []
        res = [f.upper().replace(' ', '_') for f in flags]
        assert(all(f in ALL_FLAGS for f in res))
        return res

    def parse_flags(self, flags, ace):
        ace['flags'] = self.parse_flags_enum_values(flags)

    def pretty_flags(self, ace):
        return get_pretty_flags(ace['flags'])

    def ace_flags_equal(self, ace, flags):
        return set(ace['flags']) == set(self.parse_flags_enum_values(flags))

    def find_grant_position(self, acl):
        '''
        Return a canonically ordered position for a new allow ACE.

        The canonical ACL order is explicit (non-inherited) denies followed by
        explicit allows followed by denies inherited from parent, allows
        inherited from parent, denies inherited from grandparent, and so on.
        So, any position between the last explicit deny and the first inherited
        ACE is correct.  This method chooses the position immediately before
        the first inherited ACE.

        Note that this has no special logic to locate a correct position for a
        new ACE that has the inherited flag set. The correct position for such
        an ACE is not well defined given that the ACE is not actually inherited.
        If the position is not specified explicitly, it might as well go where
        a normal explicit ACE would.
        '''
        for pos, ace in enumerate(acl):
            if INHERITED_FLAG in ace['flags']:
                return pos
        return len(acl)

def pretty_acl(body):
    # Print "None" if there are no POSIX special permissions
    if len(body['posix_special_permissions']) == 0:
        body['posix_special_permissions'] = ['None']

    res = "Control: {}\n".format(", ".join(
        [r.replace("_", " ").capitalize()
            for r in body['control']]))
    res += "Posix Special Permissions: {}\n".format(", ".join(
        [r.replace("_", " ").capitalize()
            for r in body['posix_special_permissions']]))
    res += "\nPermissions:\n"
    res += AclEditor(FsAceTranslator(), body['aces']).pretty_str()
    return res

def pretty_acl_response(response, print_json):
    if print_json:
        return str(response)
    else:
        body, _etag = response
        return pretty_acl(body)


class GetAclCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_get_acl"
    DESCRIPTION = "Get file ACL"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to file", type=str_decode)
        group.add_argument("--id", help="File ID", type=str)
        parser.add_argument("--snapshot", help="Snapshot ID to read from",
            type=int)
        parser.add_argument("--json", action='store_true', default=False,
            help="Print raw response JSON")

    @staticmethod
    def main(conninfo, credentials, args):
        print pretty_acl_response(
            fs.get_acl_v2(conninfo, credentials, args.path, args.id,
                snapshot=args.snapshot),
            args.json)

class SetAclCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_set_acl"
    DESCRIPTION = "Set file ACL"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to file", type=str)
        group.add_argument("--id", help="File ID", type=str)
        parser.add_argument("--file",
            help="Local file containing ACL JSON with control flags, "
                 "ACEs, and optionally special POSIX permissions "
                 "(sticky, setgid, setuid)",
            required=False, type=str)

    @staticmethod
    def main(conninfo, credentials, args):
        if not bool(args.file):
            raise ValueError('Must specify --file')

        with open(args.file) as f:
            contents = f.read()
            try:
                acl = json.loads(contents)
            except ValueError as e:
                raise ValueError("Error parsing ACL data: %s\n" % str(e))

        print fs.set_acl_v2(
            conninfo, credentials, acl, path=args.path, id_=args.id)

ALLOWED_TYPE = "ALLOWED"
DENIED_TYPE = "DENIED"

TYPE_CHOICES = sorted([tc.capitalize() for tc in [ALLOWED_TYPE, DENIED_TYPE]])
FLAG_CHOICES = sorted([fc.replace('_', ' ').capitalize() for fc in ALL_FLAGS])

SPECIAL_POSIX_PERMISSIONS = ['STICKY_BIT', 'SET_GID', 'SET_UID']
SPECIAL_POSIX_CHOICES = [sp.replace('_', ' ').capitalize()
    for sp in SPECIAL_POSIX_PERMISSIONS]

def _put_new_acl(fs_mod, conninfo, creds, acl, editor, etag, args):
    acl = {
        'control': acl['control'],
        'posix_special_permissions': acl['posix_special_permissions'],
        'aces': editor.acl
    }
    result = fs_mod.set_acl_v2(
        conninfo, creds, acl, path=args.path, id_=args.id, if_match=etag)

    if args.json:
        return str(result)
    else:
        body, etag = result
        return u'New permissions:\n{}'.format(
            AclEditor(FsAceTranslator(), body['aces']).pretty_str())

def do_add_entry(fs_mod, conninfo, creds, args):
    acl, etag = fs_mod.get_acl_v2(conninfo, creds, args.path, args.id)

    translator = FsAceTranslator()
    editor = AclEditor(translator, acl['aces'])
    ace_type = translator.parse_type_enum_value(args.type)
    if ace_type == ALLOWED_TYPE:
        editor.grant([args.trustee], args.rights, args.flags, args.insert_after)
    else:
        assert ace_type == DENIED_TYPE
        editor.deny([args.trustee], args.rights, args.flags, args.insert_after)

    return _put_new_acl(fs_mod, conninfo, creds, acl, editor, etag, args)

def do_remove_entry(fs_mod, conninfo, creds, args):
    acl, etag = fs_mod.get_acl_v2(conninfo, creds, args.path, args.id)

    editor = AclEditor(FsAceTranslator(), acl['aces'])
    editor.remove(position=args.position,
        trustee=args.trustee,
        ace_type=args.type,
        rights=args.rights,
        flags=args.flags,
        allow_multiple=args.all_matching)

    if args.dry_run:
        return u'New permissions would be:\n{}'.format(editor.pretty_str())

    return _put_new_acl(fs_mod, conninfo, creds, acl, editor, etag, args)

def do_modify_entry(fs_mod, conninfo, creds, args):
    acl, etag = fs_mod.get_acl_v2(conninfo, creds, args.path, args.id)
    editor = AclEditor(FsAceTranslator(), acl['aces'])
    editor.modify(args.position,
        args.old_trustee, args.old_type, args.old_rights, args.old_flags,
        args.new_trustee, args.new_type, args.new_rights, args.new_flags,
        args.all_matching)

    if args.dry_run:
        return u'New permissions would be:\n{}'.format(editor.pretty_str())

    return _put_new_acl(fs_mod, conninfo, creds, acl, editor, etag, args)

def do_set_posix(fs_mod, conninfo, creds, args):
    bits = [p.replace(' ', '_').upper() for p in args.permissions]
    assert all(b in SPECIAL_POSIX_PERMISSIONS for b in bits)

    # XXX iain: PATCH would be real nice...
    acl, etag = fs_mod.get_acl_v2(conninfo, creds, args.path, args.id)
    acl['posix_special_permissions'] = bits
    result = fs_mod.set_acl_v2(
        conninfo, creds, acl, path=args.path, id_=args.id, if_match=etag)

    return pretty_acl_response(result, args.json)

class ModifyAclCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_modify_acl"
    DESCRIPTION = "Modify file ACL"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to file", type=str_decode)
        group.add_argument("--id", help="File ID", type=str)

        parser.add_argument("--json", action='store_true', default=False,
            help="Print the raw JSON response.")

        subparsers = parser.add_subparsers()

        add_entry = subparsers.add_parser("add_entry",
            help="Add an entry to the file's ACL.")
        add_entry.set_defaults(function=do_add_entry)
        add_entry.add_argument(
            "-t", "--trustee", type=str_decode, required=True,
            help="The trustee to add.  e.g. Everyone, uid:1000, gid:1001, "
                 "sid:S-1-5-2-3-4, or auth_id:500")
        add_entry.add_argument("-y", "--type", type=str, required=True,
            choices=TYPE_CHOICES,
            help="Whether the trustee should be allowed or denied the "
                "given rights")
        add_entry.add_argument("-r", "--rights", type=str, nargs="+",
            required=True, metavar='RIGHT',
            help="The rights that should be allowed or denied.  Choices: "
                 + (", ".join(RIGHT_CHOICES)))
        add_entry.add_argument("-f", "--flags", type=str, nargs="*",
            metavar='FLAG', choices=FLAG_CHOICES,
            help="The flags the entry should have. Choices: "
                + (", ".join(FLAG_CHOICES)))
        # Allows specification of the position after which the new ACE will be
        # inserted.  That is, 0 will insert at the the beginning, 1 will insert
        # after the first entry, etc.
        # Hidden because overriding the default canonical position is not
        # recommended.
        add_entry.add_argument("--insert-after",
            type=int, default=None, help=argparse.SUPPRESS)

        remove_entry = subparsers.add_parser("remove_entry",
            help="Remove an entry from the file's ACL.")
        remove_entry.set_defaults(function=do_remove_entry)
        remove_entry.add_argument("-p", "--position", type=int,
            help="The position of the entry to remove.")
        remove_entry.add_argument("-t", "--trustee", type=str_decode,
            help="Remove an entry with this trustee.  e.g. Everyone, "
                 "uid:1000, gid:1001, sid:S-1-5-2-3-4, or auth_id:500")
        remove_entry.add_argument("-y", "--type", type=str,
            choices=TYPE_CHOICES, help="Remove an entry of this type")
        remove_entry.add_argument("-r", "--rights", type=str, nargs="+",
             metavar='RIGHT',
            help="Remove an entry with these rights.  Choices: "
                 + (", ".join(RIGHT_CHOICES)))
        remove_entry.add_argument("-a", "--all-matching", action='store_true',
            default=False, help="If multiple entries match the "
                "arguments, remove all of them")
        remove_entry.add_argument("-f", "--flags", type=str, nargs="*",
            metavar='FLAG', choices=FLAG_CHOICES,
            help="Remove an entry with these flags. Choices: "
                + (", ".join(FLAG_CHOICES)))
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
        modify_entry.add_argument("--old-type", type=str,
            choices=TYPE_CHOICES, help="Modify an entry of this type")
        modify_entry.add_argument("--old-rights", type=str, nargs="+",
             metavar='RIGHT',
            help="Modify an entry with these rights.  Choices: "
                 + (", ".join(RIGHT_CHOICES)))
        modify_entry.add_argument("--old-flags", type=str, nargs="*",
            metavar='FLAG', choices=FLAG_CHOICES,
            help="Modify an entry with these flags. Choices: "
                + (", ".join(FLAG_CHOICES)))
        modify_entry.add_argument("--new-trustee", type=str_decode,
            help="Set the entry to have this trustee.  e.g. Everyone, "
                 "uid:1000, gid:1001, sid:S-1-5-2-3-4, or auth_id:500")
        modify_entry.add_argument("--new-type", type=str,
            choices=TYPE_CHOICES, help="Set the type of the entry.")
        modify_entry.add_argument("--new-rights", type=str, nargs="+",
             metavar='RIGHT',
            help="Set the rights of the entry.  Choices: "
                 + (", ".join(RIGHT_CHOICES)))
        modify_entry.add_argument("--new-flags", type=str, nargs="*",
            metavar='FLAG', choices=FLAG_CHOICES,
            help="Set the flags of the entry. Choices: "
                + (", ".join(FLAG_CHOICES)))
        modify_entry.add_argument("-a", "--all-matching", action='store_true',
            default=False, help="If multiple entries match the arguments, "
                "modify all of them")
        modify_entry.add_argument(
            "-d", "--dry-run", action='store_true', default=False,
            help="Do nothing; display what the result of the change would be.")

        set_posix = subparsers.add_parser("set_posix_special_permissions",
            help="Set the Set UID, Set GID, and Sticky bits.")
        set_posix.set_defaults(function=do_set_posix)
        # Should probably just be positional, but argparse seemingly has a bug
        # where it won't accept zero choices for a positional argument.
        set_posix.add_argument("-p", "--permissions",
            choices=SPECIAL_POSIX_CHOICES, required=True, nargs='*',
            help='The special posix bits that should be set')

    @staticmethod
    def main(conninfo, credentials, args, outfile=sys.stdout, fs_mod=fs):
        outfile.write(u'{}\n'.format(
            args.function(fs_mod, conninfo, credentials, args)))

class CreateFileCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_create_file"
    DESCRIPTION = "Create a new file"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--path", type=str_decode, help="Path to parent directory")
        group.add_argument("--id", help="ID of parent directory")
        parser.add_argument(
            "--name", type=str_decode, help="New file name", required=True)

    @staticmethod
    def main(conninfo, credentials, args):
        print fs.create_file(conninfo, credentials, args.name,
            dir_path=args.path, dir_id=args.id)

class CreateDirectoryCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_create_dir"
    DESCRIPTION = "Create a new directory"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--path", type=str_decode, help="Path to parent directory")
        group.add_argument("--id", help="ID of parent directory")
        parser.add_argument(
            "--name", type=str_decode, help="New directory name", required=True)

    @staticmethod
    def main(conninfo, credentials, args):
        print fs.create_directory(conninfo, credentials, args.name,
            dir_path=args.path, dir_id=args.id)

class CreateSymlinkCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_create_symlink"
    DESCRIPTION = "Create a new symbolic link"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to parent directory")
        group.add_argument("--id", help="ID of parent directory")
        parser.add_argument("--target", help="Link target", required=True)
        parser.add_argument("--target-type", help="Link target type")
        parser.add_argument("--name", help="New symlink name", required=True)

    @staticmethod
    def main(conninfo, credentials, args):
        print fs.create_symlink(
            conninfo,
            credentials,
            args.name,
            args.target,
            dir_path=args.path,
            dir_id=args.id,
            target_type=args.target_type)

def parse_major_minor_numbers(major_minor_numbers):
    if major_minor_numbers is None:
        return None
    major, _, minor = major_minor_numbers.partition(',')
    return {
        'major': int(major),
        'minor': int(minor)
    }

class CreateUNIXFileCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_create_unix_file"
    DESCRIPTION = "Create a new pipe, character device, block device or socket"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to parent directory")
        group.add_argument("--id", help="ID of parent directory")
        parser.add_argument(
            "--major-minor-numbers", help="Major and minor numbers")
        parser.add_argument("--name", help="New file name", required=True)
        parser.add_argument(
            "--type", help="type of UNIX file to create", required=True)

    @staticmethod
    def main(conninfo, credentials, args):
        major_minor_numbers = \
            parse_major_minor_numbers(args.major_minor_numbers)
        print fs.create_unix_file(
            conninfo,
            credentials,
            name=args.name,
            file_type=args.type,
            major_minor_numbers=major_minor_numbers,
            dir_path=args.path,
            dir_id=args.id)

class CreateLinkCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_create_link"
    DESCRIPTION = "Create a new link"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to parent directory")
        group.add_argument("--id", help="ID of parent directory")
        parser.add_argument("--target", help="Link target", required=True)
        parser.add_argument("--name", help="New link name", required=True)

    @staticmethod
    def main(conninfo, credentials, args):
        print fs.create_link(conninfo, credentials, args.name,
            args.target, dir_path=args.path, dir_id=args.id)

class RenameCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_rename"
    DESCRIPTION = "Rename a file system object"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path",
            help="Path to destination parent directory")
        group.add_argument("--id", help="ID of destination parent directory")
        parser.add_argument("--source", help="Source file path", required=True)
        parser.add_argument("--name", help="New name in destination directory",
            required=True)
        parser.add_argument(
            '--clobber', action='store_true', default=False,
            help='Clobber destination if exists')

    @staticmethod
    def main(conninfo, credentials, args):
        print fs.rename(conninfo, credentials, args.name,
            args.source, dir_path=args.path, dir_id=args.id,
            clobber=args.clobber)

class DeleteCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_delete"
    DESCRIPTION = "Delete a file system object"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to file system object")
        group.add_argument("--id", help="ID of file system object")

    @staticmethod
    def main(conninfo, credentials, args):
        fs.delete(conninfo, credentials, path=args.path, id_=args.id)
        print "File system object was deleted."

class WriteFileCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_write"
    DESCRIPTION = "Write data to an object"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to file", type=str)
        group.add_argument("--id", help="File ID", type=str)
        parser.add_argument("--offset", type=int,
                            help="Offset at which to write data. If not "
                                 "specified, the existing contents of the file "
                                 "will be replaced with the given contents.")
        parser.add_argument("--file", help="File data to send", type=str)
        parser.add_argument("--create", action="store_true",
                            help="Create file before writing (fails if exists)")
        parser.add_argument("--stdin", action="store_true",
                            help="Write file from stdin")

        # TODO ADS: Remove suppress for actual release
        parser.add_argument("--stream-id", help=argparse.SUPPRESS)

    @staticmethod
    def main(conninfo, credentials, args):
        if args.id and args.create:
            raise ValueError("cannot use --create with --id")
        if args.stdin:
            if args.file:
                raise ValueError("--stdin conflicts with --file")
            elif not args.chunked:
                raise ValueError("--stdin must be sent chunked")
        elif args.file:
            if not os.path.isfile(args.file):
                raise ValueError("%s is not a file" % args.file)
        else:
            raise ValueError("Must specify --stdin or --file")

        infile = open(args.file, "rb") if args.file else sys.stdin

        if args.create:
            dirname, basename = util.unix_path_split(args.path)
            if not basename:
                raise ValueError("Path has no basename")
            fs.create_file(conninfo, credentials, basename, dirname)

        etag = None
        print fs.write_file(
            conninfo,
            credentials,
            infile,
            args.path,
            args.id,
            etag,
            args.offset,
            args.stream_id)

class ReadFileCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_read"
    DESCRIPTION = "Read an object"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to file", type=str)
        group.add_argument("--id", help="File ID", type=str)
        parser.add_argument("--snapshot", help="Snapshot ID to read from",
                            type=int)
        parser.add_argument("--offset", type=int,
                            help="Offset at which to read data. If not "
                                 "specified, read from the beginning of the "
                                 "file.")
        parser.add_argument("--length", type=int,
                            help="Amount of data to read. If not specified, "
                                 "read the entire file.")
        parser.add_argument("--file", help="File to receive data", type=str)
        parser.add_argument("--force", action='store_true',
                            help="Overwrite an existing file")
        parser.add_argument("--stdout", action='store_const', const=True,
                            help="Output data to standard out")

        # TODO ADS: Remove suppress for actual release
        parser.add_argument("--stream-id", help=argparse.SUPPRESS)

    @staticmethod
    def main(conninfo, credentials, args):
        if args.stdout:
            if args.file:
                raise ValueError("--stdout conflicts with --file")
        elif args.file:
            if os.path.exists(args.file) and not args.force:
                raise ValueError("%s already exists." % args.file)
        else:
            raise ValueError("Must specify --stdout or --file")

        if args.file is None:
            f = sys.stdout
        else:
            f = open(args.file, "wb")

        fs.read_file(conninfo, credentials, f,
            path=args.path, id_=args.id, snapshot=args.snapshot,
            offset=args.offset, length=args.length, stream_id=args.stream_id)
        # Print nothing on success (File may be output into stdout)

class ReadDirectoryCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_read_dir"
    DESCRIPTION = "Read directory"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Directory path", type=str)
        group.add_argument("--id", help="Directory ID", type=str)
        parser.add_argument("--page-size", type=int,
                            help="Max directory entries to return per request")
        parser.add_argument("--snapshot", help="Snapshot ID to read from",
                            type=int)
        parser.add_argument("--smb-pattern", type=str,
                            help="SMB style match pattern.")

    @staticmethod
    def main(conninfo, credentials, args):
        if args.page_size is not None and args.page_size < 1:
            raise ValueError("Page size must be greater than 0")

        page = fs.read_directory(conninfo, credentials,
            page_size=args.page_size,
            path=args.path,
            id_=args.id,
            snapshot=args.snapshot,
            smb_pattern=args.smb_pattern)

        print page

        next_uri = json.loads(str(page))["paging"]["next"]
        while next_uri != "":
            page = request.rest_request(conninfo, credentials, "GET", next_uri)
            print page
            next_uri = json.loads(str(page))["paging"]["next"]

class ReadDirectoryCapacityCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_read_dir_aggregates"
    DESCRIPTION = "Read directory aggregation entries"

    @staticmethod
    def options(parser):
        parser.add_argument("--path", help="Directory path", type=str,
            required=True)
        parser.add_argument("--recursive", action="store_true",
            help="Fetch recursive aggregates")
        parser.add_argument("--max-entries",
            help="Maximum number of entries to return", type=int)
        parser.add_argument("--max-depth",
            help="Maximum depth to recurse when --recursive is set", type=int)
        parser.add_argument("--order-by", choices=AGG_ORDERING_CHOICES,
            help="Specify field used for top N selection and sorting")
        parser.add_argument("--snapshot", type=int,
            help="Snapshot ID to read from")

    @staticmethod
    def main(conninfo, credentials, args):
        print fs.read_dir_aggregates(conninfo, credentials,
            args.path, args.recursive, args.max_entries, args.max_depth,
            args.order_by, snapshot=args.snapshot)

class TreeWalkCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_walk_tree"
    DESCRIPTION = "Walk file system tree"

    @staticmethod
    def options(parser):
        parser.add_argument("--path", help="Path to tree root", type=str,
                            required=False, default='/')

    @staticmethod
    def main(conninfo, credentials, args):
        for f, _etag in fs.tree_walk_preorder(conninfo, credentials, args.path):
            print '%s sz=%s owner=%s group=%s ' \
                  'owner_id_type=%s owner_id_value=%s ' \
                  'group_id_type=%s group_id_value=%s' % (
                f['path'], f['size'], f['owner'],
                f['group'], f['owner_details']['id_type'],
                str(f['owner_details']['id_value']),
                f['group_details']['id_type'],
                str(f['group_details']['id_value']))

class TreeDeleteCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_delete_tree"
    DESCRIPTION = "Delete file system tree recursively"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to tree root")
        group.add_argument("--id", help="ID of tree root")
        parser.add_argument("--force", "-f", action="store_true", help=
            "Bypass path confirmation. WARNING! Tree delete cannot be "
            "undone! It is dangerous to delete without confirmation.")

    @staticmethod
    def _get_argv0():
        # XXX dmotles: this gets patched out in unit tests because our cli tests
        # don't allow dependency injection of the argv[0] (i.e. the command)
        return sys.argv[0]

    @staticmethod
    def _status_cmd_str(conninfo, id_=None, path=None):
        cmd = [
            TreeDeleteCommand._get_argv0(),
            '--host', conninfo.host,
            '--port', str(conninfo.port),
            TreeDeleteStatusCommand.NAME,
        ]
        assert id_ or path
        if id_ is not None:
            cmd.extend(['--id', id_])
        elif path is not None:
            path = pipes.quote(path)
            cmd.extend(['--path', path])
        return ' '.join(cmd)

    @staticmethod
    def main(conninfo, credentials, args):
        if not args.force:
            if args.path is None:
                paths, _etag = fs.resolve_paths(
                    conninfo, credentials, [args.id])
                path = paths[0]['path']
            else:
                path = args.path

            aggr, _ = fs.read_dir_aggregates(conninfo, credentials, path)
            num_files = aggr["total_files"]
            size = util.pretty_bytes(int(aggr["total_capacity"]))
            message = \
                'WARNING! Tree delete cannot be undone. Are you sure that you '\
                'want to delete all {num} files (total size: {size}) in '\
                '"{path}"?'.format(num=num_files, size=size, path=path)

            if not qumulo.lib.opts.ask(TreeDeleteCommand.NAME, message):
                return # Operation cancelled

        fs.delete_tree(
            conninfo, credentials, path=args.path, id_=args.id)
        print 'Tree delete initiated! Check status with:\n{}'.format(
            TreeDeleteCommand._status_cmd_str(conninfo, args.id, args.path))

class TreeDeleteStatusCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_delete_tree_status"
    DESCRIPTION = "Status of a tree-delete job"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to tree root")
        group.add_argument("--id", help="ID of tree root")

    @staticmethod
    def main(conninfo, credentials, args):
        print fs.tree_delete_status(
            conninfo, credentials, path=args.path, id_=args.id)

class GetFileSamplesCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_file_samples"
    DESCRIPTION = "Get a number of sample files from the file system"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to query root")
        group.add_argument("--id", help="ID of query root")
        parser.add_argument("--count", type=int, required=True)
        parser.add_argument("--sample-by",
                            choices=['capacity', 'file'],
                            help="Weight sampling by the given value")

    @staticmethod
    def main(conninfo, credentials, args):
        print fs.get_file_samples(conninfo, credentials, args.path, args.count,
                                  args.sample_by, id_=args.id)

class ResolvePathsCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_resolve_paths"
    DESCRIPTION = "Resolve file IDs to paths"

    @staticmethod
    def options(parser):
        parser.add_argument("--ids", required=True, nargs="*",
            help="File IDs to resolve")
        parser.add_argument("--snapshot", help="Snapshot ID to read from",
            type=int)

    @staticmethod
    def main(conninfo, credentials, args):
        print fs.resolve_paths(conninfo, credentials, args.ids,
            snapshot=args.snapshot)

class ListLocksByFileCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_list_locks_by_file"
    DESCRIPTION = "List locks held on a particular files"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="File path", type=str)
        group.add_argument("--id", help="File ID", type=str)
        parser.add_argument("--protocol", type=str, required=True,
            choices = { p for p, t in fs.VALID_LOCK_PROTO_TYPE_COMBINATIONS },
            help="The protocol whose locks should be listed")
        parser.add_argument("--lock-type", type=str, required=True,
            choices = { t for p, t in fs.VALID_LOCK_PROTO_TYPE_COMBINATIONS },
            help="The type of lock to list.")
        parser.add_argument("--snapshot", type=str,
            help="Snapshot id of the specified file.")

    @staticmethod
    def main(conninfo, credentials, args):
        if (args.protocol, args.lock_type) not in \
                fs.VALID_LOCK_PROTO_TYPE_COMBINATIONS:
            raise ValueError(
                "Lock type {} not available for protocol {}".format(
                    args.lock_type, args.protocol))

        print json.dumps(
            fs.list_all_locks_by_file(
                conninfo,
                credentials,
                args.protocol,
                args.lock_type,
                args.path,
                args.id,
                args.snapshot),
            indent=4)

class ListLocksByClientCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_list_locks_by_client"
    DESCRIPTION = "List locks held by a particular client machine"

    @staticmethod
    def options(parser):
        parser.add_argument("--protocol", type=str, required=True,
            choices = { p for p, t in fs.VALID_LOCK_PROTO_TYPE_COMBINATIONS },
            help="The protocol whose locks should be listed")
        parser.add_argument("--lock-type", type=str, required=True,
            choices = { t for p, t in fs.VALID_LOCK_PROTO_TYPE_COMBINATIONS },
            help="The type of lock to list.")
        parser.add_argument("--name", help="Client hostname", type=str)
        parser.add_argument("--address", help="Client IP address", type=str)

    @staticmethod
    def main(conninfo, credentials, args):
        if (args.protocol, args.lock_type) not in \
                fs.VALID_LOCK_PROTO_TYPE_COMBINATIONS:
            raise ValueError(
                "Lock type {} not available for protocol {}".format(
                    args.lock_type, args.protocol))

        if args.name and (args.protocol != 'nlm'):
            raise ValueError("--name may only be specified for NLM locks")

        print json.dumps(
            fs.list_all_locks_by_client(
                conninfo,
                credentials,
                args.protocol,
                args.lock_type,
                args.name,
                args.address),
            indent=4)

class ListWaitersByFileCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_list_lock_waiters_by_file"
    DESCRIPTION = "List waiting lock requests for a particular files"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="File path", type=str)
        group.add_argument("--id", help="File ID", type=str)
        parser.add_argument("--protocol", type=str, required=True,
            choices = { p for p, t in fs.VALID_WAITER_PROTO_TYPE_COMBINATIONS },
            help="The protocol whose lock waiters should be listed")
        parser.add_argument("--lock-type", type=str, required=True,
            choices = { t for p, t in fs.VALID_WAITER_PROTO_TYPE_COMBINATIONS },
            help="The type of lock whose waiters should be listed")
        parser.add_argument("--snapshot", type=str,
            help="Snapshot id of the specified file.")

    @staticmethod
    def main(conninfo, credentials, args):
        if (args.protocol, args.lock_type) not in \
                fs.VALID_WAITER_PROTO_TYPE_COMBINATIONS:
            raise ValueError(
                "Lock type {} not available for protocol {}".format(
                    args.lock_type, args.protocol))

        print json.dumps(
            fs.list_all_waiters_by_file(
                conninfo,
                credentials,
                args.protocol,
                args.lock_type,
                args.path,
                args.id,
                args.snapshot),
            indent=4)

class ListWaitersByClientCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_list_lock_waiters_by_client"
    DESCRIPTION = "List waiting lock requests for a particular client machine"

    @staticmethod
    def options(parser):
        parser.add_argument("--protocol", type=str, required=True,
            choices = { p for p, t in fs.VALID_WAITER_PROTO_TYPE_COMBINATIONS },
            help="The protocol whose lock waiters should be listed")
        parser.add_argument("--lock-type", type=str, required=True,
            choices = { t for p, t in fs.VALID_WAITER_PROTO_TYPE_COMBINATIONS },
            help="The type of lock whose waiters should be listed")
        parser.add_argument("--name", help="Client hostname", type=str)
        parser.add_argument("--address", help="Client IP address", type=str)

    @staticmethod
    def main(conninfo, credentials, args):
        if (args.protocol, args.lock_type) not in \
                fs.VALID_WAITER_PROTO_TYPE_COMBINATIONS:
            raise ValueError(
                "Lock type {} not available for protocol {}".format(
                    args.lock_type, args.protocol))

        if args.name and (args.protocol != 'nlm'):
            raise ValueError("--name may only be specified for NLM locks")

        print json.dumps(
            fs.list_all_waiters_by_client(
                conninfo,
                credentials,
                args.protocol,
                args.lock_type,
                args.name,
                args.address),
            indent=4)

class ReleaseNLMLocksByClientCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_release_nlm_locks_by_client"
    DESCRIPTION = '''Release NLM byte range locks held by client. This method
    releases all locks held by a particular client. This is dangerous, and
    should only be used after confirming that the client is dead.'''

    @staticmethod
    def options(parser):
        parser.add_argument("--force",
            help="This command can cause corruption, add this flag to \
                release lock", action='store_true', required=False)
        parser.add_argument("--name", help="Client hostname", type=str)
        parser.add_argument("--address", help="Client IP address", type=str)

    @staticmethod
    def main(conninfo, credentials, args):
        if not args.name and not args.address:
            raise ValueError("Must specify --name or --address")

        if not args.force and not qumulo.lib.opts.ask(
                ReleaseNLMLocksByClientCommand.NAME, LOCK_RELEASE_FORCE_MSG):
            return # Operation cancelled.

        fs.release_nlm_locks_by_client(
                conninfo,
                credentials,
                args.name,
                args.address)
        params = ""
        if args.name:
            params += "owner_name: {}".format(args.name)
        if args.name and args.address:
            params += ", "
        if args.address:
            params += "owner_address: {}".format(args.address)
        print "NLM byte-range locks held by {} were released.".format(params)

class ReleaseNLMLockCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_release_nlm_lock"
    DESCRIPTION = '''Release an arbitrary NLM byte-range lock range. This is
    dangerous, and should only be used after confirming that the owning process
    has leaked the lock, and only if there is a very good reason why the
    situation should not be resolved by terminating that process.'''

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="File path", type=str)
        group.add_argument("--id", help="File ID", type=str)
        parser.add_argument("--offset", help="NLM byte-range lock offset",
                required=True, type=str)
        parser.add_argument("--size", help="NLM byte-range lock size",
                required=True, type=str)
        parser.add_argument("--owner-id", help="Owner id",
                required=True, type=str)
        parser.add_argument("--force",
                help="This command can cause corruption, add this flag to \
                        release lock", action='store_true', required=False)
        parser.add_argument("--snapshot",
            help="Snapshot ID of the specified file", type=str)

    @staticmethod
    def main(conninfo, credentials, args):
        if not args.force and not qumulo.lib.opts.ask(
                ReleaseNLMLockCommand.NAME, LOCK_RELEASE_FORCE_MSG):
            return # Operation cancelled.

        fs.release_nlm_lock(
                conninfo,
                credentials,
                args.offset,
                args.size,
                args.owner_id,
                args.path,
                args.id,
                args.snapshot)

        file_path_or_id = ""
        if args.path is not None:
            file_path_or_id = "file_path: {}".format(args.path)
        if args.id is not None:
            file_path_or_id = "file_id: {}".format(args.id)

        snapshot = ""
        if args.snapshot is not None:
            snapshot = ", snapshot: {}".format(args.snapshot)

        output = (
            "NLM byte-range lock with "
            "(offset: {0}, size: {1}, owner-id: {2}, {3}{4})"
            " was released."
            ).format(args.offset, args.size, args.owner_id,
            file_path_or_id, snapshot)

        print output

class PunchHoleCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_punch_hole"
    DESCRIPTION = '''Create a hole in a region of a file. Destroys all data
        within the hole.'''

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to file", type=str)
        group.add_argument("--id", help="File ID", type=str)
        parser.add_argument("--offset",
            help="Offset in bytes specifying the start of the hole to create",
            required=True, type=int)
        parser.add_argument("--size",
            help="Size in bytes of the hole to create",
            required=True, type=int)

        # TODO ADS: Remove suppress for actual release
        parser.add_argument("--stream-id", help=argparse.SUPPRESS)

    @staticmethod
    def main(conninfo, credentials, args):
        print fs.punch_hole(
            conninfo,
            credentials,
            args.offset,
            args.size,
            path=args.path,
            id_=args.id,
            stream_id=args.stream_id)

class GetPermissionsSettingsCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_get_permissions_settings"
    DESCRIPTION = "Get permissions settings"

    @staticmethod
    def main(conninfo, credentials, _args):
        print fs.get_permissions_settings(conninfo, credentials)

VALID_PERMISSIONS_MODES = frozenset(
    ['NATIVE', '_DEPRECATED_MERGED_V1', 'CROSS_PROTOCOL'])

def permissions_mode(arg):
    '''
    XXX US20314: Allow, but suppress the help text for, _DEPRECATED_MERGED_V1
    until it has been fully deprecated and prepared for removal. At that point,
    this custom type should be removed and SetPermissionsSettingsCommand should
    utilize argparse choices for all valid modes.
    '''
    mode = arg.upper()
    if mode in VALID_PERMISSIONS_MODES:
        return mode

    raise TypeError('Invalid argument \'%s\'' % arg)

class SetPermissionsSettingsCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_set_permissions_settings"
    DESCRIPTION = "Set permissions settings"

    @staticmethod
    def options(parser):
        parser.add_argument(
            "mode",
            help="Permissions mode to set (NATIVE or CROSS_PROTOCOL)",
            type=permissions_mode)

    @staticmethod
    def main(conninfo, credentials, args):
        print fs.set_permissions_settings(conninfo, credentials, mode=args.mode)

#                  _       _          __           _
#   _____  ___ __ | | __ _(_)_ __    / _|_ __ ___ | |_
#  / _ \ \/ / '_ \| |/ _` | | '_ \  | |_| '_ ` _ \| __|
# |  __/>  <| |_) | | (_| | | | | | |  _| | | | | | |_
#  \___/_/\_\ .__/|_|\__,_|_|_| |_| |_| |_| |_| |_|\__|
#           |_|
#  FIGLET: explain fmt
#

SINGLE_LEVEL_INDENT = ' ' * 4

class ExplainAceFormatter(object):
    '''
    Common translator for explanation ACEs in permissions explainers
    '''
    def __init__(self, indent_lvl=0):
        self.fs_ace_translator = FsAceTranslator()
        self.indent_lvl = indent_lvl

    def indent(self, s):
        return SINGLE_LEVEL_INDENT * self.indent_lvl + s

    def pretty_fs_ace(self, fs_ace):
        ace_type = self.fs_ace_translator.pretty_type(fs_ace)
        trustee = self.fs_ace_translator.pretty_trustee(fs_ace)
        rights = self.fs_ace_translator.pretty_rights(fs_ace)
        flags = self.fs_ace_translator.pretty_flags(fs_ace)

        return self.indent('{type}\t{trustee}\t{rights}{flags}'.format(
            type=ace_type,
            trustee=trustee,
            rights=rights if rights else 'None',
            flags='\t({})'.format(flags) if flags else ''))

PRETTY_HEADER_PADDING = '===='

def pretty_explain_header(conninfo, credentials, body, acl):
    settings, _etag = fs.get_permissions_settings(conninfo, credentials)
    pretty_mode = settings['mode'].replace('_', ' ').capitalize()

    header = u'Permissions Mode: {}\n'.format(pretty_mode) + \
        u'Owner: {}\n'.format(unicode(Identity(body['owner']))) + \
        u'Group: {}\n'.format(unicode(Identity(body['group_owner']))) + \
        u'\n' + \
        u'{h} Current ACL {h}\n'.format(h=PRETTY_HEADER_PADDING) + \
        u'{}\n'.format(pretty_acl(acl)) + \
        u'\n'
    return header

def pretty_explain_acl(aces, formatter):
    '''
    From @p aces, as returned by an explain API response, produce the prettified
    output for the explain ACL, providing a position to note in each ACE's
    header. e.g.,
        ==== 1 ====
        <Prettified ACE 1>

        ==== 2 ====
        <Prettified ACE 2>
        ...
        ==== N ====
        <Prettified ACE N>
    '''
    lines = []
    for idx, ace in enumerate(aces):
        lines.append(
            '{h} {p} {h}\n'.format(h=PRETTY_HEADER_PADDING, p=idx+1) + \
            formatter.pretty_explanation_ace(ace))

    return '\n\n'.join(lines)

#                  _       _                             _
#   _____  ___ __ | | __ _(_)_ __    _ __ ___   ___   __| | ___
#  / _ \ \/ / '_ \| |/ _` | | '_ \  | '_ ` _ \ / _ \ / _` |/ _ \
# |  __/>  <| |_) | | (_| | | | | | | | | | | | (_) | (_| |  __/
#  \___/_/\_\ .__/|_|\__,_|_|_| |_| |_| |_| |_|\___/ \__,_|\___|
#           |_|
#  FIGLET: explain mode
#

MODE_CLASSES = ('OWNER', 'GROUP', 'OTHER')

def select_classes_by_match_type(matches, _type):
    'Returns only the mode classes in @p matches that map to @p type'
    return [mc.upper() for mc in matches.keys() if matches[mc] == _type]

POSIX_SPECIAL_PERMISSIONS = frozenset(['STICKY_BIT', 'SET_GID', 'SET_UID'])

def pretty_mode_bits(bits_str):
    '''
    From a single digit representation of the bits, @p bits_str (e.g. '4'),
    produce the char array of its prettier form.
    Example:
        pretty_mode_bits(5) = ['r', '-', 'x']
    '''
    pretty_bits = ['-', '-', '-']
    bit_strs = 'xwr'
    for x in range(3):
        if (1 << x) & int(bits_str) != 0:
            pretty_bits[2 - x] = bit_strs[x]

    return pretty_bits

def pretty_posix_mode(
        mode_octal, posix_special, file_type='FS_FILE_TYPE_FILE'):
    '''
    @param mode_octal       {string}    Non-special POSIX mode to prettify
    @param posix_special    {list}      POSIX special permissions bitfield vals
    @param file_type        {string}    File-type enum value
    @return                 {string}    Full posix mode in pretty form,
                                        e.g. 'drwSr--r-t'
    '''
    assert all(p in POSIX_SPECIAL_PERMISSIONS for p in posix_special)

    u = mode_octal[-3]
    g = mode_octal[-2]
    o = mode_octal[-1]

    segments = [
        ['d' if file_type == 'FS_FILE_TYPE_DIRECTORY' else '-'],
        pretty_mode_bits(u),
        pretty_mode_bits(g),
        pretty_mode_bits(o)
    ]

    # Incorporate posix_special into the pretty mode segments
    if 'STICKY_BIT' in posix_special:
        segments[-1][2] = 'T' if segments[-1][2] != 'x' else 't'
    if 'SET_GID' in posix_special:
        segments[-2][2] = 'S' if segments[-2][2] != 'x' else 's'
    if 'SET_UID' in posix_special:
        segments[-3][2] = 'S' if segments[-3][2] != 'x' else 's'

    return ''.join(''.join(s) for s in segments)

class ExplainPosixModeAceFormatter(ExplainAceFormatter):
    '''
    Translator for the explanation ACEs in fs_acl_explain_posix_mode
    '''
    def pretty_matches(self, ace):
        '''
        Gathers the mode segment match information for each mode class in the
        provided @p ace, and prints a summary of which segments were matched and
        why. This will return None if the ace is inherit-only, or if there is
        an unexpected set of matches, which should be impossible in the API
        contract.
        '''
        if ace['is_inherit_only']:
            return None

        matches = collections.OrderedDict(
            (mc, ace[mc.lower() + '_rights']['match']) for mc in MODE_CLASSES)
        match_lines = []

        if all(m == 'NONE' for m in matches.values()):
            match_lines = ['Matched: NONE']

        if all(m == 'EVERYONE' for m in matches.values()):
            match_lines = ['Matched: EVERYONE']

        equivalents = select_classes_by_match_type(matches, 'EQUIVALENT')
        potentially_affected = select_classes_by_match_type(
            matches, 'POTENTIALLY_AFFECTED')

        if equivalents:
            match_lines.append('Matched: ' + ','.join(equivalents))
        if potentially_affected:
            match_lines.append('Potentially affects rights for: ' +
                ','.join(potentially_affected))

        match_lines = [self.indent(m) for m in match_lines]
        return '\n'.join(match_lines) if match_lines else None

    def pretty_cumulative_rights(self, ace):
        '''
        If @p ace is explaining an ALLOW ACE, reports the cumulative allowed
        rights for each mode segment, otherwise denied. This will return None
        if the ace is inherit-only.
        '''
        if ace['is_inherit_only']:
            return None

        assert ace['ace']['type'].upper() in (ALLOWED_TYPE, DENIED_TYPE)
        allowed = ace['ace']['type'].upper() == ALLOWED_TYPE

        cumulative_rights_lines = []
        if allowed:
            cumulative_rights_lines.append(self.indent(
                'Cumulative rights allowed:'))
        else:
            cumulative_rights_lines.append(self.indent(
                'Cumulative rights denied:'))

        for mc in MODE_CLASSES:
            self.indent_lvl += 1
            rights = ace[mc.lower() + '_rights']
            cumulative = rights['cumulative_allowed'] if allowed \
                else rights['cumulative_denied']

            rights_str = 'None'
            if cumulative != []:
                rights_str = self.fs_ace_translator.pretty_rights(
                    ace={ 'rights': cumulative })

            cumulative_rights_lines.append(self.indent(
                mc.capitalize() + ': ' + rights_str))
            self.indent_lvl -= 1

        return '\n'.join(cumulative_rights_lines)

    def pretty_mode_bits_granted(self, ace):
        '''
        Represent mode-bit contribution of @p ace in human-readable
        form. If the ace is inherit-only, or if the mode_bits_granted was some
        representation of zero (e.g. '0', '0000', '00000'), return None.
        Example output:
            Mode Bit Contribution: --x--x--x
        '''
        if ace['is_inherit_only'] or \
                all(b == '0' for b in ace['mode_bits_granted']):
            return None

        # N.B. First bit of the pretty mode is discarded here as ACEs don't
        # contribute to the first file-type bit
        return self.indent('Mode Bit Contribution: {}'.format(
            pretty_posix_mode(ace['mode_bits_granted'], posix_special=[])[1:]))

    def pretty_explanation_ace(self, ace):
        '''
        Produces the full explanation for the given ACE. The prettified FS ACE
        will always be printed, but the other explanation fields will be
        prettified and printed only if the ACE is not inherit-only.
        '''
        lines = []
        lines.append(self.pretty_fs_ace(ace['ace']))
        self.indent_lvl += 1
        if ace['is_inherit_only']:
            lines.append(self.indent('Inherit-Only: No effect'))
            self.indent_lvl -= 1
            return '\n'.join(lines)

        matches = self.pretty_matches(ace)
        if matches:
            lines.append(matches)

        cumulative = self.pretty_cumulative_rights(ace)
        if cumulative:
            lines.append(cumulative)

        mode_contribution = self.pretty_mode_bits_granted(ace)
        if mode_contribution:
            lines.append(mode_contribution)

        self.indent_lvl -= 1
        return '\n'.join(lines)

def _print_explain_posix_mode_response(body, attrs, outfile):
    outfile.write(u'Mode derivation from ACL for "{}":\n\n'.format(
        attrs['path']))
    outfile.write('{}\n'.format(
        pretty_explain_acl(body['annotated_acl'],
        ExplainPosixModeAceFormatter())))
    outfile.write('\n')
    outfile.write(
        'Final Derived Mode: {}\n'.format(
            pretty_posix_mode(
                body['mode'],
                body['posix_special_permissions'],
                file_type=attrs['type'])))

class AclExplainPosixModeCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_acl_explain_posix_mode"
    DESCRIPTION = \
        "[Beta] Explain the derivation of POSIX mode from a file's ACL"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to file/directory", type=str)
        group.add_argument("--id", help="File ID", type=str)

        parser.add_argument("--json", action="store_true",
            help="Print JSON representation of POSIX mode derivation")

    @staticmethod
    def main(conninfo, credentials, args, outfile=sys.stdout):
        response = fs.acl_explain_posix_mode(
            conninfo, credentials, path=args.path, id_=args.id)
        if args.json:
            print response
            return

        attrs, _etag = fs.get_file_attr(
            conninfo, credentials, path=args.path, id_=args.id)
        acl, _etag = fs.get_acl_v2(
            conninfo, credentials, path=args.path, id_=args.id)

        outfile.write(pretty_explain_header(
            conninfo, credentials, response.data, acl))
        _print_explain_posix_mode_response(response.data, attrs, outfile)

#                  _       _              _                         _
#   _____  ___ __ | | __ _(_)_ __     ___| |__  _ __ ___   ___   __| |
#  / _ \ \/ / '_ \| |/ _` | | '_ \   / __| '_ \| '_ ` _ \ / _ \ / _` |
# |  __/>  <| |_) | | (_| | | | | | | (__| | | | | | | | | (_) | (_| |
#  \___/_/\_\ .__/|_|\__,_|_|_| |_|  \___|_| |_|_| |_| |_|\___/ \__,_|
#           |_|
#  FIGLET: explain chmod
#

CHMOD_ACTIONS = ('COPY_ACE', 'MODIFY_ACE', 'INSERT_ACE', 'REMOVE_ACE')
# The possible longest string in the left column of an explanation entry, for
# alignment purposes
MAX_COLUMN = 'Rights removed'

class ExplainSetModeAceFormatter(ExplainAceFormatter):
    '''
    Translator for the explanation entries in fs_acl_explain_chmod. Note that
    each entry is not an ACE per se, but corresponds to an action taken on an
    ACE, old or new, to achieve the resulting ACL.
    '''
    def pretty_action(self, entry):
        '''
        Returns the string for the action performed on a given explanation entry
        '''
        if entry['action'] not in CHMOD_ACTIONS:
            return None
        if entry['action'] == 'COPY_ACE':
            return 'Use original entry'

        action = entry['action'].split('_')[0].title()
        return action + ' entry'

    def pretty_explanation_row(self, field_name, value):
        return '{field}:{pad}\t{value}'.format(
            field=field_name,
            pad=' ' * (len(MAX_COLUMN) - len(field_name)),
            value=value)

    def pretty_trustee_match(self, entry):
        match = entry['source_trustee_match']
        if 'NO_MATCH' in match:
            return None

        trustee = self.fs_ace_translator.pretty_trustee(entry.get('source_ace'))
        pretty_mapping = {
            'NON_POSIX': 'non-POSIX trustee',
            'POSIX_OWNER': 'POSIX owner',
            'POSIX_GROUP_OWNER': 'POSIX group owner',
            'POSIX_OTHERS': 'POSIX others'
        }
        matches = [pretty_mapping[m] for m in match]

        return '\'{trustee}\' matches {matches}'.format(
            trustee=trustee, matches=', '.join(matches))

    def pretty_explanation_ace(self, entry):
        '''
        Produces the prettified explanation entry. Only print the fields that
        are relevant to the action.
        '''
        lines = []
        lines.append(
            self.pretty_explanation_row('Action', self.pretty_action(entry)))
        if entry['source_ace'] is not None:
            lines.append(self.pretty_explanation_row(
                'Source entry', self.pretty_fs_ace(entry['source_ace'])))
        if len(entry['source_trustee_match']) > 0:
            lines.append(self.pretty_explanation_row(
                'Trustee match', self.pretty_trustee_match(entry)))
        if len(entry['rights_removed']) > 0:
            lines.append(self.pretty_explanation_row(
                'Rights removed',
                get_pretty_rights_string(set(entry['rights_removed']))))
        if len(entry['flags_removed']) > 0:
            lines.append(self.pretty_explanation_row(
                'Flags removed', get_pretty_flags(entry['flags_removed'])))
        if len(entry['flags_added']) > 0:
            lines.append(self.pretty_explanation_row(
                'Flags added', get_pretty_flags(entry['flags_added'])))
        if entry['result_ace']:
            lines.append(self.pretty_explanation_row(
                'New entry',
                self.pretty_fs_ace(entry['result_ace'])))
        lines.append(self.pretty_explanation_row('Reason', entry['reason']))
        return '\n'.join(lines)

def summarize_class_rights(body, mode_segment):
    rights = set(body['{}_rights_from_mode'.format(mode_segment)])
    rights_str = 'None' if not rights else get_pretty_rights_string(rights)
    return SINGLE_LEVEL_INDENT + '{segment}: {rights}\n'.format(
        segment=mode_segment, rights=rights_str)

def _print_verbose_explain_chmod_info(body, outfile):
    outfile.write(
        'Rights POSIX trustees always keep (never produced by mode): '
        '{}\n'.format(
            get_pretty_rights_string(set(body['not_produced_by_any_mode']))))
    outfile.write(
        'Rights non-POSIX trustees always keep (never displayed in mode): '
        '{}\n'.format(
            get_pretty_rights_string(set(body['not_visible_in_mode']))))
    outfile.write(
        'Maximum rights on non-POSIX ACEs '
        '(trustee not POSIX owner/group/everyone):\n')
    outfile.write(SINGLE_LEVEL_INDENT + 'Allow ACE: {}\n'.format(
        get_pretty_rights_string(set(body['max_extra_ace_allow']))))
    outfile.write(SINGLE_LEVEL_INDENT + 'Deny ACE: {}\n'.format(
        get_pretty_rights_string(set(body['max_extra_ace_deny']))))
    outfile.write('\n')

def _print_explain_chmod_response(body, mode, verbose, outfile):
    outfile.write('Mode {} translates to rights:\n'.format(mode))
    outfile.write(summarize_class_rights(body, 'owner'))
    outfile.write(summarize_class_rights(body, 'group'))
    outfile.write(summarize_class_rights(body, 'other'))
    outfile.write('\n')
    if verbose:
        _print_verbose_explain_chmod_info(body, outfile)
    outfile.write(
        'Steps for applying mode {} to original permissions:\n'.format(mode))
    outfile.write('{}\n'.format(
        pretty_explain_acl(body['annotated_aces'],
        ExplainSetModeAceFormatter())))
    outfile.write('\n')
    outfile.write('{h} Resulting ACL {h}\n'.format(h=PRETTY_HEADER_PADDING))
    outfile.write(pretty_acl(body['result_acl']))
    outfile.write('\n\n')

def posix_mode(mode):
    '''
    Custom argparse type for POSIX mode. Accepts the following formats:
        0744
        rwxr--r--
    '''
    mode_regex = re.compile(r'([r-][w-][x-]){3,3}')
    mode_map = { 'r': 4, 'w': 2, 'x': 1, '-': 0 }
    if mode_regex.match(mode):
        mode_out = "0"
        for bit in textwrap.wrap(mode, 3):
            bit_value = sum([mode_map[v] for v in bit])
            mode_out += str(bit_value)
        return mode_out

    mode_out = str(oct(int(mode, base=8)))
    # If needed, prepend zeros for a friendlier mode display
    if len(mode_out) < 4:
        mode_out = '0' * (4 - len(mode_out)) + mode_out

    return mode_out

class AclExplainSetModeCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_acl_explain_chmod"
    DESCRIPTION = \
        "[Beta] Explain how setting a POSIX mode would affect a file's ACL"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", type=str, help="Path to file/directory")
        group.add_argument("--id", type=str, help="File ID")

        parser.add_argument("--mode", required=True, type=posix_mode,
            help="POSIX mode to hypothetically apply (e.g., 0744, rwxr--r--)")
        parser.add_argument("-v", "--verbose", action="store_true",
            help="Print more information in output")
        parser.add_argument("--json", action="store_true",
            help="Print JSON representation of POSIX mode derivation")

    @staticmethod
    def main(conninfo, credentials, args, outfile=sys.stdout):
        response = fs.acl_explain_chmod(
            conninfo, credentials, path=args.path, id_=args.id, mode=args.mode)
        if args.json:
            print response
            return

        outfile.write(pretty_explain_header(
            conninfo, credentials, response.data, response.data['initial_acl']))
        _print_explain_chmod_response(
            response.data, args.mode, args.verbose, outfile)

#                  _       _              _       _     _
#   _____  ___ __ | | __ _(_)_ __    _ __(_) __ _| |__ | |_ ___
#  / _ \ \/ / '_ \| |/ _` | | '_ \  | '__| |/ _` | '_ \| __/ __|
# |  __/>  <| |_) | | (_| | | | | | | |  | | (_| | | | | |_\__ \
#  \___/_/\_\ .__/|_|\__,_|_|_| |_| |_|  |_|\__, |_| |_|\__|___/
#           |_|                             |___/
#  FIGLET: explain rights
#

def _print_explain_rights_ace(ace, aligner):
    ace_translator = FsAceTranslator()
    ace_detail_fmt = '{ace_key} {ace_value}'
    # Print "type 'trustee' rights, (flags)" without padding:
    aligner.add_line('{ace_key} {0} \'{1}\' {2} {3}',
        ace_translator.pretty_type(ace['ace']),
        ace_translator.pretty_trustee(ace['ace']),
        ace_translator.pretty_rights(ace['ace']),
        '' if not ace['ace']['flags'] else
            '({})'.format(ace_translator.pretty_flags(ace['ace'])),
        ace_key='Entry:')
    aligner.add_line(ace_detail_fmt,
        ace_key='Trustee Matches:', ace_value=ace['trustee_matches'])
    if not ace['trustee_matches']:
        return
    if ace['skipped_inherit_only']:
        aligner.add_line(ace_detail_fmt,
            ace_key='Inherit-only:', ace_value='True; ACE has no effect')
        return
    if ace['ace']['type'] == ALLOWED_TYPE:
        aligner.add_line(ace_detail_fmt,
            ace_key='Allowed so far:',
            ace_value=get_pretty_rights_string(
                set(ace['cumulative_allowed'])))
    else:
        aligner.add_line(ace_detail_fmt,
            ace_key='Denied so far:',
            ace_value=get_pretty_rights_string(
                set(ace['cumulative_denied'])))

def _add_implicit_rights_line(aligner, type_, rights, no_rights_override=None):
    if rights:
        rights_str = get_pretty_rights_string(set(rights))
    elif no_rights_override:
        rights_str = no_rights_override
    else:
        rights_str = 'Not {}'.format(type_)
    aligner.add_line('{implicit_type} {implicit_rights}',
        implicit_type='{} rights:'.format(type_), implicit_rights=rights_str)

def _print_implicit_rights(body, aligner):
    _add_implicit_rights_line(
        aligner, 'Administrator', body.get('admin_priv_rights'))
    _add_implicit_rights_line(
        aligner,
        'File Owner',
        body.get('implicit_owner_rights'),
        None if not body.get('implicit_owner_rights_suppressed_by_ace')
            else 'Overridden by explicit Owner Rights ACE')
    _add_implicit_rights_line(aligner,
        'Parent Directory', body.get('implicit_rights_from_parent'), 'None')

RIGHT_EXPLANATIONS = {
    'READ': 'Read file data or list directory',
    'READ_EA': 'Read extended attributes',
    'READ_ATTR': 'Read attributes',
    'READ_ACL': 'Read access control list',
    'WRITE_EA': 'Write extended attributes',
    'WRITE_ATTR': 'Write attributes',
    'WRITE_ACL': 'Write access control list',
    'CHANGE_OWNER': 'Change file owner',
    'WRITE_GROUP': 'Change file group-owner',
    'DELETE': 'Delete this object',
    'EXECUTE': 'Execute file or traverse directory',
    'MODIFY': 'Modify file data',
    'EXTEND': 'Append to file',
    'ADD_FILE': 'Add file to directory',
    'ADD_SUBDIR': 'Add directory to directory',
    'DELETE_CHILD': 'Delete any of a directory\'s immediate children',
    'SYNCHRONIZE': 'Meaningless, exists for compatibility',
}

def _print_explain_rights_response(body, outfile):
    outfile.write('File Owner: {}\nFile Group Owner: {}\n\n'.format(
        Identity(body['owner']), Identity(body['group_owner'])))

    user_str = str(Identity(body['requestor']['user']))

    aligner = util.TextAligner()
    aligner.add_line('ACL evaluation steps for \'{}\':'.format(user_str))
    for idx, ace in enumerate(body['annotated_aces'], 1):
        aligner.add_line('{0} {idx} {0}', PRETTY_HEADER_PADDING, idx=idx)
        with aligner.indented():
            _print_explain_rights_ace(ace, aligner)

    aligner.add_line('')
    aligner.add_line('Implicit Rights for \'{}\':'.format(user_str))
    with aligner.indented():
        _print_implicit_rights(body, aligner)

    aligner.add_line('')
    aligner.add_line('Rights that would be granted to \'{}\':'.format(user_str))
    with aligner.indented():
        for right in body['effective_rights']:
            verbose = RIGHT_EXPLANATIONS.get(right, 'Unknown')
            aligner.add_line('{granted_right} {verbose_right}',
                granted_right=API_RIGHTS_TO_CLI.get(right, right),
                verbose_right='({})'.format(verbose))

    aligner.write(outfile)

class AclExplainRightsCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_acl_explain_rights"
    DESCRIPTION = textwrap.dedent('''\
        [Beta] Explain how rights are granted to a user for a file.

        Note that this command does not discover the user's groups and related
        identities when computing rights. To provide this information, use the
        -g argument.''')

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--path", type=str_decode, help="Path to file/directory")
        group.add_argument("--id", type=str, help="File ID")

        parser.add_argument("-u", "--user", required=True, type=str_decode,
            help="User for whom to explain rights. e.g. Alice, uid:1000, "
                 "sid:S-1-5-2-3-4, or auth_id:500")
        parser.add_argument("-p", "--primary-group", required=True,
            type=str_decode, help="User's primary group. See -u for examples.")
        parser.add_argument(
            "-g", "--groups", type=str_decode, nargs="*", metavar="ID",
            help="User's additional groups and related identities. See -u for "
                 "examples.")
        parser.add_argument("--json", action="store_true",
            help="Print JSON representation of rights explanation.")

    @staticmethod
    def main(conninfo, credentials, args, outfile=sys.stdout):
        response = fs.acl_explain_rights(
            conninfo,
            credentials,
            path=args.path,
            id_=args.id,
            user=args.user,
            group=args.primary_group,
            ids=args.groups)

        if args.json:
            print response
        else:
            _print_explain_rights_response(response.data, outfile)
