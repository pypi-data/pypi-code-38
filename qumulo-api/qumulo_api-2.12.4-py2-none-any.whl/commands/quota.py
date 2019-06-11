# Copyright (c) 2016 Qumulo, Inc.
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
import qumulo.rest.quota as quota
import qumulo.rest.fs as fs
import qumulo.lib.request as request
import qumulo.lib.util as util

class GetQuotasCommand(qumulo.lib.opts.Subcommand):
    NAME = "quota_list_quotas"
    DESCRIPTION = "List all directory quotas"

    @staticmethod
    def options(parser):
        parser.add_argument("--page-size", type=int,
                            help="Max quota entries to return per request")

    @staticmethod
    def main(conninfo, credentials, args):
        if args.page_size is not None and args.page_size < 1:
            raise ValueError("Page size must be greater than 0")
        for res in quota.get_all_quotas_with_status(
                conninfo, credentials, args.page_size):
            print res

class GetQuotaCommand(qumulo.lib.opts.Subcommand):
    NAME = "quota_get_quota"
    DESCRIPTION = "Get a directory quota"

    @staticmethod
    def options(parser):
        parser.add_argument("--path", type=str, help="Path name")
        parser.add_argument("--id", type=str, help="File ID")

    @staticmethod
    def main(conninfo, credentials, args):
        if args.id and args.path:
            raise ValueError("--path conflicts with --id")
        elif not args.id and not args.path:
            raise ValueError("Must specify --path or --id")

        id_num = fs.get_file_attr(
                     conninfo, credentials, path=args.path)[0]['id'] \
                 if args.path else args.id
        print quota.get_quota_with_status(conninfo, credentials, id_num)

class CreateQuotaCommand(qumulo.lib.opts.Subcommand):
    NAME = "quota_create_quota"
    DESCRIPTION = "Create a directory quota"

    @staticmethod
    def options(parser):
        parser.add_argument("--path", type=str, help="Path name")
        parser.add_argument("--id", type=str, help="File ID")
        parser.add_argument("--limit", type=str, required=True,
            help='Quota limit in bytes. Both base-10 and base-2 shorthand' \
            ' names are accepted: GB or GiB, TB or TiB (e.g. 50GB)')

    @staticmethod
    def main(conninfo, credentials, args):
        if args.id and args.path:
            raise ValueError("--path conflicts with --id")
        elif not args.id and not args.path:
            raise ValueError("Must specify --path or --id")

        if args.path:
            # if by path failed, use bad id number (1) and allow create to fail
            try:
                id_num = fs.get_file_attr(conninfo, credentials,
                    path=args.path)[0]['id']
            except request.RequestError:
                id_num = 1
        else:
            id_num = args.id

        limit_in_bytes = util.get_bytes(args.limit)
        print quota.create_quota(conninfo, credentials, id_num, limit_in_bytes)

class UpdateQuotaCommand(qumulo.lib.opts.Subcommand):
    NAME = "quota_update_quota"
    DESCRIPTION = "Update a directory quota"

    @staticmethod
    def options(parser):
        parser.add_argument("--path", type=str, help="Path name")
        parser.add_argument("--id", type=str, help="File ID")
        parser.add_argument("--limit", type=str, required=True,
            help='Quota limit in bytes. Both base-10 and base-2 shorthand' \
            ' names are accepted: GB or GiB, TB or TiB (e.g. 50GB)')

    @staticmethod
    def main(conninfo, credentials, args):
        if args.id and args.path:
            raise ValueError("--path conflicts with --id")
        elif not args.id and not args.path:
            raise ValueError("Must specify --path or --id")

        id_num = fs.get_file_attr(conninfo, credentials,
                path=args.path)[0]['id'] if args.path else args.id

        limit_in_bytes = util.get_bytes(args.limit)
        print quota.update_quota(conninfo, credentials, id_num, limit_in_bytes)

class DeleteQuotaCommand(qumulo.lib.opts.Subcommand):
    NAME = "quota_delete_quota"
    DESCRIPTION = "Delete a directory quota"

    @staticmethod
    def options(parser):
        parser.add_argument("--path", type=str, help="Path name")
        parser.add_argument("--id", type=str, help="File ID")

    @staticmethod
    def main(conninfo, credentials, args):
        if args.id and args.path:
            raise ValueError("--path conflicts with --id")
        elif not args.id and not args.path:
            raise ValueError("Must specify --path or --id")

        id_num = fs.get_file_attr(conninfo, credentials,
                path=args.path)[0]['id'] if args.path else args.id
        quota.delete_quota(conninfo, credentials, id_num)
