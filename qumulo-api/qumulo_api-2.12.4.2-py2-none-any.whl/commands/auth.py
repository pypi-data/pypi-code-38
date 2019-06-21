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
import json
import sys
import textwrap

import qumulo.lib.auth
import qumulo.lib.opts
import qumulo.lib.identity_util as id_util
import qumulo.rest.auth as auth
import qumulo.rest.users as users
import qumulo.rest.groups as groups

def list_user(conninfo, credentials, user_id):
    user = users.list_user(conninfo, credentials, user_id)
    user_groups = users.list_groups_for_user(conninfo, credentials,
        user_id)

    # Print out results only on success of both rest calls
    print '%s\nUser %d is a member of following groups: %s' % (
        user, int(user_id), user_groups)

def list_group(conninfo, credentials, group_id):
    group = groups.list_group(conninfo, credentials, group_id)
    members = groups.group_get_members(conninfo, credentials, group_id)

    print '%s\nGroup %d has the following members: %s' % (
        group, int(group_id), members)

def get_expanded_identity_information_for_user(conninfo, credentials, auth_id):
    user_info = auth.auth_id_to_all_related_identities(
            conninfo, credentials, auth_id)

    # Print out results only on success of both rest calls
    return 'Expanded identity information for user %d: %s' % (
        int(auth_id), user_info)

def get_expanded_identity_information_for_group(conninfo, credentials, auth_id):
    group_info = auth.auth_id_to_all_related_identities(
            conninfo, credentials, auth_id)

    # Print out results only on success of both rest calls
    return 'Expanded identity information for group %d: %s' % (
        int(auth_id), group_info)

def get_user_group_info_msg(conninfo, credentials, auth_id):
    user_groups = users.list_groups_for_user(conninfo, credentials,
        auth_id)
    return 'User %d is a member of following groups: %s' % (
        int(auth_id), user_groups)

def get_group_members_msg(conninfo, credentials, group_id):
    group = groups.list_group(conninfo, credentials, group_id)
    members = groups.group_get_members(conninfo, credentials, group_id)

    return '%s\nGroup %d has the following members: %s' % (
        group, int(group_id), members)

#  _   _                  ____                                          _
# | | | |___  ___ _ __   / ___|___  _ __ ___  _ __ ___   __ _ _ __   __| |___
# | | | / __|/ _ \ '__| | |   / _ \| '_ ` _ \| '_ ` _ \ / _` | '_ \ / _` / __|
# | |_| \__ \  __/ |    | |__| (_) | | | | | | | | | | | (_| | | | | (_| \__ \
#  \___/|___/\___|_|     \____\___/|_| |_| |_|_| |_| |_|\__,_|_| |_|\__,_|___/
#

class ChangePasswordCommand(qumulo.lib.opts.Subcommand):
    NAME = "change_password"
    DESCRIPTION = "Change your password"

    @staticmethod
    def options(parser):
        parser.add_argument(
            "-o", "--old-password", type=str, default=None,
            help="Your old password (insecure, visible via ps)")
        parser.add_argument(
            "-p", "--new-password", type=str, default=None,
            help="Your new password (insecure, visible via ps)")

    @staticmethod
    def main(conninfo, credentials, args):
        if args.old_password is not None:
            old_password = args.old_password
        else:
            old_password = \
                qumulo.lib.opts.read_password(prompt="Old password: ")

        if args.new_password is not None:
            new_password = args.new_password
        else:
            new_password = \
                qumulo.lib.opts.read_password(prompt="New password: ")
            new_password_confirm = \
                qumulo.lib.opts.read_password(prompt="Confirm new password: ")
            if new_password != new_password_confirm:
                print 'Passwords don\'t match!'
                return 1

        auth.change_password(
            conninfo, credentials, old_password, new_password)
        print "Your password has been changed."

class SetUserPasswordCommand(qumulo.lib.opts.Subcommand):
    NAME = "auth_set_password"
    DESCRIPTION = "Set a user's password"

    @staticmethod
    def options(parser):
        parser.add_argument("--id", type=str, default=None, required=True,
            help="Name or ID of user to modify")
        parser.add_argument("-p", "--password", type=str, default=None,
            help="The user's new password (insecure, visible via ps)")

    @staticmethod
    def main(conninfo, credentials, args):
        user_id = users.get_user_id(conninfo, credentials, args.id)

        if args.password is not None:
            password = args.password
        else:
            password = \
                qumulo.lib.opts.read_password("New password for %s: " % args.id)

        users.set_user_password(conninfo, credentials, user_id.data,
            password)
        print "Changed password for %s" % args.id

class ListUsersCommand(qumulo.lib.opts.Subcommand):
    NAME = "auth_list_users"
    DESCRIPTION = "List all users"

    @staticmethod
    def main(conninfo, credentials, _args):
        print users.list_users(conninfo, credentials)

class ListUserCommand(qumulo.lib.opts.Subcommand):
    NAME = "auth_list_user"
    DESCRIPTION = "List a user"

    @staticmethod
    def options(parser):
        parser.add_argument("--id", type=str, default=None, required=True,
            help="Name or ID of user to lookup")

    @staticmethod
    def main(conninfo, credentials, args):
        user_id = int(users.get_user_id(conninfo, credentials, args.id).data)
        user = users.list_user(
            conninfo, credentials, user_id)

        # Get all related group info
        group_info_msg = get_user_group_info_msg(conninfo, credentials, user_id)

        # Get all related IDs
        related_info_msg = get_expanded_identity_information_for_user(
            conninfo, credentials, user_id)

        print user
        print group_info_msg
        print related_info_msg

class AddUserCommand(qumulo.lib.opts.Subcommand):
    NAME = "auth_add_user"
    DESCRIPTION = "Add a new user"

    @staticmethod
    def options(parser):
        parser.add_argument("--name", type=str, default=None,
            help="New user's name (windows style)", required=True)
        parser.add_argument("--primary-group", type=str, default=0,
            help="name or id of primary group (default is Users)")
        parser.add_argument("--uid", type=int, default=None,
            help="optional NFS uid")
        parser.add_argument("--home-directory", type=str, default=None,
            help="optional home directory")
        parser.add_argument("-p", "--password", type=str, nargs='?',
            const=True, default=None,
            help="Set user password; reads password from terminal if omitted")

    @staticmethod
    def main(conninfo, credentials, args):
        if args.password is True:
            password = qumulo.lib.opts.read_password(args.name)
        elif args.password is not None:
            password = args.password

        group_id = groups.get_group_id(
            conninfo, credentials, args.primary_group)

        res = users.add_user(
            conninfo,
            credentials,
            args.name,
            group_id.data,
            args.uid,
            args.home_directory)

        # Set new user's password, ignoring output.
        if args.password is not None:
            user_id = int(res.lookup('id'))
            users.set_user_password(conninfo, credentials, user_id,
                password)

        # Get all related IDs
        related_info_msg = get_expanded_identity_information_for_user(
            conninfo, credentials, int(res.lookup('id')))

        print res
        print related_info_msg

class ModUserCommand(qumulo.lib.opts.Subcommand):
    NAME = "auth_mod_user"
    DESCRIPTION = "Modify a user"

    @staticmethod
    def options(parser):
        parser.add_argument("--id", type=str, default=None, required=True,
            help="Name or ID of user to modify")
        parser.add_argument("--name", default=None, help="Change user's name")
        parser.add_argument("--primary-group", type=str, default=None,
            help="Change the user's primary group")
        parser.add_argument("--uid", type=str, default=None,
            help="Change the user's NFS uid (or specify \"none\" to remove)")
        parser.add_argument("--add-group", type=str, default=None,
            help="Add this user to a group")
        parser.add_argument("--remove-group", type=str, default=None,
            help="Remove this user from a group")
        parser.add_argument("--home-directory", type=str, default=None,
            help="Change the user's home directory path. "
                 "(or specify \"none\" to remove")

    @staticmethod
    def main(conninfo, credentials, args):
        # Get the user object
        user_id = int(users.get_user_id(conninfo, credentials, args.id).data)

        response = users.list_user(conninfo, credentials, user_id)
        user_info, etag = response

        # Modify the user object according to specified arguments
        name = user_info['name']
        if args.name is not None:
            name = args.name

        primary_group = user_info['primary_group']
        if args.primary_group is not None:
            primary_group = str(groups.get_group_id(
                conninfo, credentials, args.primary_group).data)

        uid = user_info['uid']
        if args.uid is not None:
            uid = args.uid.strip()
            if uid.lower() == 'none':
                uid = ''

        home_directory = user_info['home_directory']
        if args.home_directory is not None:
            if args.home_directory.lower().strip() == "none":
                home_directory = None
            else:
                home_directory = args.home_directory

        # Set the user object, ignore output
        users.modify_user(
            conninfo,
            credentials,
            user_id,
            name,
            primary_group,
            uid,
            home_directory,
            etag)

        # Add specified groups, ignore output
        if args.add_group:
            group_id = groups.get_group_id(conninfo, credentials,
                args.add_group)
            groups.group_add_member(conninfo, credentials,
                group_id.data, user_id)

        # Remove specified groups, ignore output
        if args.remove_group:
            group_id = groups.get_group_id(conninfo, credentials,
                args.remove_group)
            groups.group_remove_member(conninfo, credentials,
                group_id.data, user_id)

        # Get all related group info
        group_info_msg = get_user_group_info_msg(conninfo, credentials, user_id)

        # Get all related IDs
        related_info_msg = get_expanded_identity_information_for_user(
            conninfo, credentials, user_id)

        print users.list_user(conninfo, credentials, user_id)
        print group_info_msg
        print related_info_msg

class DeleteUserCommand(qumulo.lib.opts.Subcommand):
    NAME = "auth_delete_user"
    DESCRIPTION = "Delete a user"

    @staticmethod
    def options(parser):
        parser.add_argument("--id", type=str, default=None, required=True,
            help="Name or ID of user to delete")

    @staticmethod
    def main(conninfo, credentials, args):
        user_id = users.get_user_id(conninfo, credentials, args.id)
        users.delete_user(conninfo, credentials, user_id.data)
        print "User was deleted."

#   ____
#  / ___|_ __ ___  _   _ _ __
# | |  _| '__/ _ \| | | | '_ \
# | |_| | | | (_) | |_| | |_) |
#  \____|_|  \___/ \__,_| .__/
#                       |_|
#   ____                                          _
#  / ___|___  _ __ ___  _ __ ___   __ _ _ __   __| |___
# | |   / _ \| '_ ` _ \| '_ ` _ \ / _` | '_ \ / _` / __|
# | |__| (_) | | | | | | | | | | | (_| | | | | (_| \__ \
#  \____\___/|_| |_| |_|_| |_| |_|\__,_|_| |_|\__,_|___/
#
class ListGroupsCommand(qumulo.lib.opts.Subcommand):
    NAME = "auth_list_groups"
    DESCRIPTION = "List all groups"

    @staticmethod
    def main(conninfo, credentials, _args):
        print groups.list_groups(conninfo, credentials)

class ListGroupCommand(qumulo.lib.opts.Subcommand):
    NAME = "auth_list_group"
    DESCRIPTION = "List a group"

    @staticmethod
    def options(parser):
        parser.add_argument("--id", type=str, default=None, required=True,
            help="Name or ID of group to list")

    @staticmethod
    def main(conninfo, credentials, args):
        group_id = int(groups.get_group_id(conninfo, credentials, args.id).data)

        group_info_msg = get_group_members_msg(conninfo, credentials, group_id)

        related_info_msg = get_expanded_identity_information_for_group(
            conninfo, credentials, group_id)

        print group_info_msg
        print related_info_msg

class AddGroupCommand(qumulo.lib.opts.Subcommand):
    NAME = "auth_add_group"
    DESCRIPTION = "Add a new group"

    @staticmethod
    def options(parser):
        parser.add_argument("--name", type=str, required=True,
            help="New group's name (windows style)")
        parser.add_argument("--gid", type=int, default=None,
            help="Optional NFS gid")

    @staticmethod
    def main(conninfo, credentials, args):
        group_info = groups.add_group(conninfo, credentials, args.name,
            args.gid)

        related_info_msg = get_expanded_identity_information_for_group(
            conninfo, credentials, group_info.lookup('id'))

        print group_info
        print related_info_msg

class ModGroupCommand(qumulo.lib.opts.Subcommand):
    NAME = "auth_mod_group"
    DESCRIPTION = "Modify a group"

    @staticmethod
    def options(parser):
        parser.add_argument("--id", type=str, default=None, required=True,
            help="Name or ID of group to modify")
        parser.add_argument("--name", default=None, help="Change group's name")
        parser.add_argument("--gid", type=str, default=None,
            help="Change the user's NFS gid (or specify \"none\" to remove)")

    @staticmethod
    def main(conninfo, credentials, args):
        # Get the group object
        group_id = groups.get_group_id(conninfo, credentials, args.id)
        group_info, etag = groups.list_group(conninfo, credentials,
            group_id.data)

        # Modify the group object according to specified arguments
        name = group_info['name']
        if args.name is not None:
            name = args.name

        gid = group_info['gid']
        if args.gid is not None:
            gid = args.gid.strip()
            if gid.lower() == 'none':
                gid = ''

        # Set the group object, ignore output
        groups.modify_group(conninfo, credentials, group_id.data,
            name, gid, etag)

        # Print out the new group object
        group_info_msg = get_group_members_msg(
            conninfo, credentials, group_id.data)

        related_info_msg = get_expanded_identity_information_for_group(
            conninfo, credentials, group_id.data)

        print group_info_msg
        print related_info_msg

class DeleteGroupCommand(qumulo.lib.opts.Subcommand):
    NAME = "auth_delete_group"
    DESCRIPTION = "Delete a group"

    @staticmethod
    def options(parser):
        parser.add_argument("--id", type=str, default=None, required=True,
            help="Name or ID of group to delete")

    @staticmethod
    def main(conninfo, credentials, args):
        group_id = groups.get_group_id(conninfo, credentials, args.id)
        groups.delete_group(conninfo, credentials, group_id.data)
        print "Group was deleted."

class GetAllRelatedIdentitiesCommand(qumulo.lib.opts.Subcommand):
    NAME = 'auth_get_all_related_identities'
    DESCRIPTION = 'Get all identities related to the given ID.'

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--auth-id", help="Get all auth_ids related to this auth_id")
        group.add_argument(
            "--username",
            help="Get all identities related to this local username")
        group.add_argument(
            "--uid", help="Get all identities related to this POSIX UID")
        group.add_argument(
            "--gid", help="Get all identities related to this POSIX GID")
        group.add_argument(
            "--sid", help="Get all identities related to this SID")

    @staticmethod
    def main(conninfo, credentials, args):

        if (args.auth_id is not None):
            print auth.auth_id_to_all_related_identities(
                conninfo, credentials, args.auth_id)
        elif (args.username is not None):
            print auth.local_username_to_all_related_identities(
                conninfo, credentials, args.username)
        elif (args.uid is not None):
            print auth.posix_uid_to_all_related_identities(
                conninfo, credentials, args.uid)
        elif (args.gid is not None):
            print auth.posix_gid_to_all_related_identities(
                conninfo, credentials, args.gid)
        elif (args.sid is not None):
            print auth.sid_to_all_related_identities(
                conninfo, credentials, args.sid)

class ClearCacheCommand(qumulo.lib.opts.Subcommand):
    NAME = 'auth_clear_cache'
    DESCRIPTION = 'Clear all cached authorization information'

    @staticmethod
    def main(conninfo, credentials, _args):
        auth.clear_cache(conninfo, credentials)


class FindUserCommand(qumulo.lib.opts.Subcommand):
    NAME = 'auth_find_identity'
    DESCRIPTION = textwrap.dedent('''\
        Find all representations of an auth_id.

        An auth_id is a unique, Qumulo-specific representation of an identity.
        This command will not show equivalent identities with different auth_ids
        (e.g., a UID and a SID that are linked by Active Directory Posix
        Extensions).

        SEE ALSO
        auth_get_all_related_identities - to find all representations of an
        identity, including those that do not have the same auth_id.''')

    @staticmethod
    def options(parser):
        parser.formatter_class=argparse.RawDescriptionHelpFormatter
        parser.add_argument('identifier', nargs='?',
            help='A name or a SID, optionally qualified with a domain prefix '
            '(e.g "local:name", "world:Everyone", "ldap_user:name", '
            '"ldap_group:name", or "ad:name") or an ID type (e.g. '
            '"uid:1001", "gid:2001", "auth_id:513", "SID:S-1-1-0").')
        parser.add_argument('--auth-id', type=int, required=False,
            help='Find all external representations for an internal QSFS '
            'identifier.')
        parser.add_argument('--uid', type=int, required=False,
            help='Find the auth_id that will be used internally when a UID '
            'is written over NFS, and any other representations that would '
            'produce that auth_id.')
        parser.add_argument('--gid', type=int, required=False,
            help='Find the auth_id that will be used internally when a GID '
            'is written over NFS, and any other representations that would '
            'produce that auth_id.')
        parser.add_argument('--sid', required=False,
            help='Find the auth_id that will be used internally when a SID '
            'is written over SMB, and any other representations that would '
            'produce that auth_id.')
        parser.add_argument('--name', required=False,
            help='Find an auth_id that is uniquely identified by the given '
            'name. Names of Active Directory users and groups will produce '
            'the auth_id that is a representation of that principal\'s SID. '
            'AD names may be unqualified, qualified with NetBIOS name (e.g. '
            'DOMAIN\user), or a universal principal name (e.g. ' +
            'user@domain.example.com). Names of LDAP users or groups will '
            'produce the auth_id that is a representation of that ' +
            'principal\'s UID or GID.  LDAP names may be either login names, '
            'or distinguished names (e.g. CN=John Doe,OU=users,DC=example,'
            'DC=com). Names of cluster-local users and groups will produce '
            'the auth_id assigned to that user or group.')
        parser.add_argument(
            '--domain', required=False, choices=[
                id_util.LOCAL_DOMAIN,
                id_util.WORLD_DOMAIN,
                id_util.POSIX_USER_DOMAIN,
                id_util.POSIX_GROUP_DOMAIN,
                id_util.AD_DOMAIN],
            help='Specify which auth_id domain is sought. This can be useful ' +
            'when looking up a duplicated name (e.g. if there is an AD user ' +
            'and cluster-local user with the same name) to specify which of ' +
            'the identifiers is meant.')
        parser.add_argument(
            '--json', action='store_true', default=False,
            help='Print result as JSON object.')

    @staticmethod
    def main(conninfo, credentials, args):
        api_id = {}
        if args.identifier is not None:
            api_id = id_util.Identity(args.identifier).dictionary()
        if args.auth_id is not None:
            api_id['auth_id'] = str(args.auth_id)
        if args.uid is not None:
            api_id['uid'] = args.uid
        if args.gid is not None:
            api_id['gid'] = args.gid
        if args.sid is not None:
            api_id['sid'] = args.sid
        if args.name is not None:
            api_id['name'] = args.name
        if args.domain is not None:
            api_id['domain'] = args.domain

        res = auth.find_identity(conninfo, credentials, **api_id)
        if args.json:
            print res
            return

        print('domain: {}'.format(res.data['domain']))
        if res.data['name'] is not None:
            print(u'name: {}'.format(res.data['name']))
        print('auth_id: {}'.format(res.data['auth_id']))
        if res.data['uid'] is not None:
            print('UID: {}'.format(res.data['uid']))
        if res.data['gid'] is not None:
            print('GID: {}'.format(res.data['gid']))
        if res.data['sid'] is not None:
            print('SID: {}'.format(res.data['sid']))

#                            _       __ _                _
#  _   _ ___  ___ _ __    __| | ___ / _(_)_ __   ___  __| |
# | | | / __|/ _ \ '__|  / _` |/ _ \ |_| | '_ \ / _ \/ _` |
# | |_| \__ \  __/ |    | (_| |  __/  _| | | | |  __/ (_| |
#  \__,_|___/\___|_|     \__,_|\___|_| |_|_| |_|\___|\__,_|
#                              _
#  _ __ ___   __ _ _ __  _ __ (_)_ __   __ _ ___
# | '_ ` _ \ / _` | '_ \| '_ \| | '_ \ / _` / __|
# | | | | | | (_| | |_) | |_) | | | | | (_| \__ \
# |_| |_| |_|\__,_| .__/| .__/|_|_| |_|\__, |___/
#                 |_|   |_|            |___/
#  FIGLET: user_defined_mappings
#

class UserDefinedMappingsGetCommand(qumulo.lib.opts.Subcommand):
    NAME = 'auth_get_user_defined_mappings'
    DESCRIPTION = \
        'Get the configured set of AD/LDAP static user defined mappings.'

    @staticmethod
    def main(conninfo, credentials, _args):
        print auth.user_defined_mappings_get(conninfo, credentials)

class UserDefinedMappingsSetCommand(qumulo.lib.opts.Subcommand):
    NAME = 'auth_set_user_defined_mappings'
    DESCRIPTION = \
        'Replace the configured set of AD/LDAP static identity mappings.'

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--file", help="JSON-encoded file containing mappings.", type=str)
        group.add_argument(
            "--stdin",
            action="store_true",
            help="Read JSON-encoded mappings from stdin")

    @staticmethod
    def main(conninfo, credentials, args):
        infile = open(args.file, "rb") if args.file else sys.stdin
        mappings = json.load(infile)
        auth.user_defined_mappings_set(conninfo, credentials, mappings)
