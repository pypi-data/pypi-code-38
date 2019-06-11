# Copyright (c) 2019 Qumulo, Inc.
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

import qumulo.lib.auth
import qumulo.lib.opts
import qumulo.rest.audit as audit

class GetAuditLogConfig(qumulo.lib.opts.Subcommand):
    NAME = 'audit_get_config'
    DESCRIPTION = 'Get audit configuration'

    @staticmethod
    def main(conninfo, credentials, _args):
        print audit.get_config(conninfo, credentials)

class SetAuditLogConfig(qumulo.lib.opts.Subcommand):
    NAME = 'audit_set_config'
    DESCRIPTION = 'Change audit configuration'

    @staticmethod
    def options(parser):
        enabled_group = parser.add_mutually_exclusive_group(required=False)
        enabled_group.set_defaults(enabled=None)
        enabled_group.add_argument(
            '--enable',
            '-e',
            dest='enabled',
            action='store_true',
            help='Enable audit log.')
        enabled_group.add_argument(
            '--disable',
            '-d',
            dest='enabled',
            action='store_false',
            help='Disable audit log.')

        parser.add_argument(
            '--server-address',
            '-s',
            type=str,
            help='The IP address, hostname, or fully qualified domain name of' \
                'your remote syslog server.')

        parser.add_argument(
            '--server-port',
            '-p',
            type=int,
            help='The port to connect to on your remote syslog server.')

    @staticmethod
    def main(conninfo, credentials, args):
        print audit.set_config(
                conninfo,
                credentials,
                enabled=args.enabled,
                server_address=args.server_address,
                server_port=args.server_port)

class GetAuditLogStatus(qumulo.lib.opts.Subcommand):
    NAME = 'audit_get_status'
    DESCRIPTION = 'Get audit log status'

    @staticmethod
    def main(conninfo, credentials, _args):
        print audit.get_status(conninfo, credentials)
