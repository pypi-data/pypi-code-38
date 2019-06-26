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

import qumulo.lib.opts
import qumulo.lib.util as util
import qumulo.rest.fs as fs
import qumulo.rest.ftp as ftp

class FtpGetStatus(qumulo.lib.opts.Subcommand):
    NAME = "ftp_get_status"
    DESCRIPTION = "Get FTP server settings and status"

    @staticmethod
    def main(conninfo, credentials, _args):
        print ftp.get_status(conninfo, credentials)

class FtpModifySettings(qumulo.lib.opts.Subcommand):
    NAME = "ftp_modify_settings"
    DESCRIPTION = "Set FTP server settings"

    @staticmethod
    def options(parser):
        parser.add_argument(
            '--enabled',
            type=util.bool_from_string,
            metavar='{true,false}',
            required=False)

        parser.add_argument(
            '--check-remote-host',
            type=util.bool_from_string,
            metavar='{true,false}',
            required=False)

        parser.add_argument(
            '--log-operations',
            type=util.bool_from_string,
            metavar='{true,false}',
            required=False)

        parser.add_argument(
            '--chroot-users',
            type=util.bool_from_string,
            metavar='{true,false}',
            required=False)

        parser.add_argument(
            '--allow-unencrypted-connections',
            type=util.bool_from_string,
            metavar='{true,false}',
            required=False)

        parser.add_argument(
            '--expand-wildcards',
            type=util.bool_from_string,
            metavar='{true,false}',
            required=False)

        group = parser.add_mutually_exclusive_group()

        group.add_argument(
            '--anonymous-user-as-local-user',
            type=fs.LocalUser,
            required=False)

        group.add_argument(
            '--anonymous-user-none', action='store_true', required=False)

        group.add_argument('--greeting', type=str, required=False)

    @staticmethod
    def main(conninfo, credentials, args):
        anonymous_user = None
        if args.anonymous_user_none:
            anonymous_user = 'none'
        else:
            anonymous_user = args.anonymous_user_as_local_user

        if args.enabled is None \
            and args.check_remote_host is None \
            and args.log_operations is None \
            and args.chroot_users is None \
            and args.allow_unencrypted_connections is None \
            and args.expand_wildcards is None \
            and anonymous_user is None \
            and args.greeting is None:
            raise ValueError("must provide at least one argument")

        print ftp.modify_settings(
            conninfo,
            credentials,
            enabled=args.enabled,
            check_remote_host=args.check_remote_host,
            log_operations=args.log_operations,
            chroot_users=args.chroot_users,
            allow_unencrypted_connections=args.allow_unencrypted_connections,
            expand_wildcards=args.expand_wildcards,
            anonymous_user=anonymous_user,
            greeting=args.greeting)
