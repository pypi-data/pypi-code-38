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

import argparse
import datetime as dt
import re

import qumulo.lib.opts
import qumulo.rest.fs as fs
import qumulo.rest.snapshot as snapshot

EXPIRATION_HELP_MSG_TEMPLATE = ("Time at which to expire the snapshot. "
    "Providing an empty string {}indicates the snapshot should never be "
    "expired. Format according to RFC 3339, which is a normalized subset of "
    "ISO 8601. See http://tools.ietf.org/rfc/rfc3339.txt, section 5.6 for "
    "ABNF.")

SNAP_TTL_HELP = ("Duration after which to expire the snapshot, in format "
    "<quantity><units>, where <quantity> is a positive integer less than "
    "100 and <units> is one of [months, weeks, days, hours, minutes],"
    "e.g. 5days or 1hours. Empty string indicates the snapshot should never"
    "expire.")

POLICY_TTL_HELP = ("Duration after which to expire snapshots created by this "
    "policy, in format <quantity><units>, where <quantity> is a positive "
    "integer less than 100 and <units> is one of [months, weeks, days, hours, "
    "minutes], e.g. 5days or 1hours. Empty string indicates snapshots should "
    "never expire.")

PERIOD_HELP = ('How often to take a snapshot, in the format <quantity><units>, '
    'where <quantity> is a positive integer less than 100 and <units> is one '
    'of [hours, minutes], e.g. 5minutes or 6hours.')

def expiration_msg(is_create):
    omit_msg = ""
    if (is_create):
        omit_msg = "or omitting this argument "
    return EXPIRATION_HELP_MSG_TEMPLATE.format(omit_msg)

class CreateSnapshotCommand(qumulo.lib.opts.Subcommand):
    NAME = "snapshot_create_snapshot"

    DESCRIPTION = "Create a new snapshot."

    @staticmethod
    def options(parser):
        parser.add_argument("-n", "--name", type=str, default=None,
            help="Name of the snapshot.")

        group = parser.add_mutually_exclusive_group(required=False)
        group.add_argument("-e", "--expiration", type=str, default=None,
            help=expiration_msg(True))
        group.add_argument("-t", "--time-to-live", type=str, default=None,
            help=SNAP_TTL_HELP)

        group = parser.add_mutually_exclusive_group(required=False)
        group.add_argument("--path", type=str, default=None,
            help="Path to directory to snapshot.")
        group.add_argument("--id", type=str, default=None,
            help="ID of directory to snapshot.")

    @staticmethod
    def main(conninfo, credentials, args):
        print snapshot.create_snapshot(
            conninfo, credentials,
            args.name, args.expiration, args.time_to_live, args.path, args.id)

class ModifySnapshotCommand(qumulo.lib.opts.Subcommand):
    NAME = "snapshot_modify_snapshot"

    DESCRIPTION = "Modify an existing snapshot."

    @staticmethod
    def options(parser):
        parser.add_argument("-i", "--id", type=str, required=True,
            help="ID of the snapshot.")
        group = parser.add_mutually_exclusive_group(required=False)
        group.add_argument("-e", "--expiration", type=str, default=None,
            help=expiration_msg(False))
        group.add_argument("-t", "--time-to-live", type=str, default=None,
            help=SNAP_TTL_HELP)

    @staticmethod
    def main(conninfo, credentials, args):
        print snapshot.modify_snapshot(
            conninfo, credentials, args.id, args.expiration, args.time_to_live)

class ListAllSnapshotsCommand(qumulo.lib.opts.Subcommand):
    NAME = "snapshot_list_snapshots"

    DESCRIPTION = "Lists all snapshots."

    @staticmethod
    def options(parser):
        parser.add_argument("--all", action="store_true",
            help="Include snapshots currently being deleted")

    @staticmethod
    def main(conninfo, credentials, args):
        print snapshot.list_snapshots(
            conninfo, credentials, include_in_delete=args.all)

class GetSnapshotCommand(qumulo.lib.opts.Subcommand):
    NAME = "snapshot_get_snapshot"

    DESCRIPTION = "Gets a single snapshot."

    @staticmethod
    def options(parser):
        parser.add_argument("-i", "--id", type=int, required=True,
            help="Identifier of the snapshot to list.")

    @staticmethod
    def main(conninfo, credentials, args):
        print snapshot.get_snapshot(conninfo, credentials, args.id)

class ListAllSnapshotStatusesCommand(qumulo.lib.opts.Subcommand):
    NAME = 'snapshot_list_statuses'

    DESCRIPTION = "List all snapshot statuses."

    @staticmethod
    def main(conninfo, credentials, _args):
        print snapshot.list_snapshot_statuses(conninfo, credentials)

class GetSnapshotStatusCommand(qumulo.lib.opts.Subcommand):
    NAME = 'snapshot_get_status'

    DESCRIPTION = 'Gets a single snapshot status.'

    @staticmethod
    def options(parser):
        parser.add_argument("-i", "--id", type=int, required=True,
            help="Identifier of the snapshot.")

    @staticmethod
    def main(conninfo, credentials, args):
        print snapshot.get_snapshot_status(conninfo, credentials, args.id)

class DeleteSnapshotCommand(qumulo.lib.opts.Subcommand):
    NAME = "snapshot_delete_snapshot"

    DESCRIPTION = "Deletes a single snapshot."

    @staticmethod
    def options(parser):
        parser.add_argument("-i", "--id", type=int, required=True,
            help="Identifier of the snapshot to delete.")

    @staticmethod
    def main(conninfo, credentials, args):
        snapshot.delete_snapshot(conninfo, credentials, args.id)

ALLOWED_DAYS = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'ALL']

def get_on_days(days_of_week):
    days = [day.strip().upper() for day in days_of_week.split(',')]

    if 'ALL' in days:
        if len(days) > 1:
            raise ValueError(
                'ALL cannot be used in conjunction with other days')

        # API parlance for "ALL"
        return ['EVERY_DAY']

    if not set(days).issubset(set(ALLOWED_DAYS)):
        raise ValueError(
            'Invalid days: {}; allowed days are: {}'.format(days, ALLOWED_DAYS))

    return days

def get_schedule_info(creation_schedule, time_to_live_str):
    schedule = {}
    if creation_schedule is not None:
        schedule.update({
            # TODO bgebert: Change once we have multiple schedules per policy.
            'creation_schedule': creation_schedule,
        })
    if time_to_live_str is not None:
        schedule.update({'expiration_time_to_live' : time_to_live_str})
    return schedule

def parse_period(period_str):
    m = re.search(r'(\d+)(\w+)', period_str)
    value = int(m.group(1))
    units_str = m.group(2).lower()
    if units_str in ('minute', 'minutes'):
        units = 'FIRE_IN_MINUTES'
    elif units_str in ('hour', 'hours'):
        units = 'FIRE_IN_HOURS'
    else:
        raise ValueError(PERIOD_HELP)
    return value, units

def get_schedule_hourly_or_less(args):
    try:
        start_time = dt.datetime.strptime(
            args.start_time if args.start_time is not None else '0:0',
            '%H:%M')
    except ValueError:
        raise ValueError('Bad format for start time')
    try:
        end_time = dt.datetime.strptime(
            args.end_time if args.end_time is not None else '23:59',
            '%H:%M')
    except ValueError:
        raise ValueError('Bad format for end time')
    if start_time > end_time:
        raise ValueError('Start time must be less than end time')

    interval_value, interval_units = parse_period(args.period)

    return {
        'frequency': 'SCHEDULE_HOURLY_OR_LESS',
        'timezone': args.timezone,
        'on_days': get_on_days(args.days_of_week),
        'window_start_hour': start_time.hour,
        'window_start_minute': start_time.minute,
        'window_end_hour': end_time.hour,
        'window_end_minute': end_time.minute,
        'fire_every_interval': interval_units,
        'fire_every': interval_value,
    }

def create_hourly_or_less(conninfo, credentials, args):
    print snapshot.create_policy(
        conninfo, credentials,
        args.name,
        get_schedule_info(
            get_schedule_hourly_or_less(args),
            args.time_to_live if args.time_to_live else ''),
        args.file_id,
        args.enabled)

def get_schedule_daily(args):
    try:
        at_time_of_day = dt.datetime.strptime(args.at, '%H:%M')
    except ValueError:
        raise ValueError('Bad format for time of day')

    return {
        'frequency': 'SCHEDULE_DAILY_OR_WEEKLY',
        'timezone': args.timezone,
        'on_days': get_on_days(args.days_of_week),
        'hour': at_time_of_day.hour,
        'minute': at_time_of_day.minute,
    }

def create_daily(conninfo, credentials, args):
    print snapshot.create_policy(
        conninfo, credentials,
        args.name,
        get_schedule_info(
            get_schedule_daily(args),
            args.time_to_live if args.time_to_live else ''),
        args.file_id,
        args.enabled)

def get_schedule_monthly(args):
    try:
        at_time_of_day = dt.datetime.strptime(args.at, '%H:%M')
    except ValueError:
        raise ValueError('Bad format for time of day')

    return {
        'frequency': 'SCHEDULE_MONTHLY',
        'timezone': args.timezone,
        'day_of_month': 128 if args.last_day_of_month else args.day_of_month,
        'hour': at_time_of_day.hour,
        'minute': at_time_of_day.minute,
    }

def create_monthly(conninfo, credentials, args):
    print snapshot.create_policy(
        conninfo, credentials,
        args.name,
        get_schedule_info(
            get_schedule_monthly(args),
            args.time_to_live if args.time_to_live else ''),
        args.file_id,
        args.enabled)

def add_hourly_specific_args(hourly_parser):
    hourly_parser.add_argument('-s', '--start-time',
        type=str, default='0:00',
        help='Do not take snapshots before this 24 hour time of day.')
    hourly_parser.add_argument('-e', '--end-time',
        type=str, default='23:59',
        help='Do not take snapshots after this 24 hour time of day.')
    hourly_parser.add_argument('-p', '--period', type=str, required=True,
        help=PERIOD_HELP)

def add_monthly_specific_args(monthly_parser):
    day_group = monthly_parser.add_mutually_exclusive_group(required=True)
    day_group.add_argument('-d', '--day-of-month', type=int,
        help='The day of the month on which to take a snapshot.')
    day_group.add_argument('-l', '--last-day-of-month', action='store_true',
        help='Take a snapshot on the last day of the month.')

def add_general_schedule_args(schedule_parser):
    schedule_parser.add_argument('-z', '--timezone', type=str, default='UTC',
        help='The timezone in which the schedule should be interpreted ' \
            '(e.g. America/Los_Angeles or UTC). See the time_list_timezones ' \
            'qq command for a complete list of supported timezones.')

# Shared by hourly and daily subcommands
hourly_daily_common_parser = argparse.ArgumentParser(add_help=False)
hourly_daily_common_parser.add_argument(
    '-d', '--days-of-week', type=str, default='ALL',
    help='Days of the week to allow snapshots. Comma separated list ' \
            '(e.g. MON,TUE,WED,THU,FRI,SAT,SUN,ALL).')

# Shared by daily and monthly subcommands
daily_monthly_common_parser = argparse.ArgumentParser(add_help=False)
daily_monthly_common_parser.add_argument(
    '-a', '--at', type=str, required=True,
    help='Take a snapshot at this 24 hour time of day (e.g. 20:00).')


class CreatePolicyCommand(qumulo.lib.opts.Subcommand):
    NAME = 'snapshot_create_policy'

    DESCRIPTION = 'Create a new snapshot scheduling policy.'

    @staticmethod
    def options(parser):
        subparsers = parser.add_subparsers()

        # Shared by all subcommands
        common_parser = argparse.ArgumentParser(add_help=False)
        common_parser.add_argument('-n', '--name', type=str, required=True,
            help='Name of the policy.')
        common_parser.add_argument(
            '-t', '--time-to-live', type=str, default=None,
            help=POLICY_TTL_HELP)
        add_general_schedule_args(common_parser)

        # Enabled?
        group = common_parser.add_mutually_exclusive_group(required=False)
        group.add_argument(
            '--enabled', dest='enabled', action='store_true',
            default=argparse.SUPPRESS,
            help='Create policy enabled (This is the default).')
        group.add_argument(
            '--disabled', dest='enabled', action='store_false',
            default=argparse.SUPPRESS,
            help='Create policy disabled.')
        parser.set_defaults(enabled=None)

        # Directory
        group = common_parser.add_mutually_exclusive_group(required=False)
        group.add_argument("--path", type=str, default=None,
            help="Path of directory upon which to take snapshots.")
        group.add_argument("--file-id", type=str, default=None,
            help="ID of directory upon which to take snapshots.")

        # Hourly or less subparser
        hourly_parser = subparsers.add_parser('hourly_or_less',
            parents=[common_parser, hourly_daily_common_parser],
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        add_hourly_specific_args(hourly_parser)
        hourly_parser.set_defaults(func=create_hourly_or_less)

        # Daily subparser
        daily_parser = subparsers.add_parser('daily',
            parents=[
                common_parser,
                hourly_daily_common_parser,
                daily_monthly_common_parser],
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        daily_parser.set_defaults(func=create_daily)

        # Monthly subparser
        monthly_parser = subparsers.add_parser('monthly',
            parents=[common_parser, daily_monthly_common_parser],
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        add_monthly_specific_args(monthly_parser)
        monthly_parser.set_defaults(func=create_monthly)

    @staticmethod
    def main(conninfo, credentials, args):
        if args.path:
            attr = fs.get_attr(conninfo, credentials, args.path)
            args.file_id = attr.lookup('file_number')

        args.func(conninfo, credentials, args)

def modify_non_schedule_fields(conninfo, credentials, args):
    print snapshot.modify_policy(
        conninfo, credentials,
        args.id,
        name=args.name,
        source_file_id=args.file_id,
        schedule_info=get_schedule_info(None, args.time_to_live),
        enabled=args.enabled)

def modify_hourly(conninfo, credentials, args):
    print snapshot.modify_policy(
        conninfo, credentials,
        args.id,
        name=args.name,
        source_file_id=args.file_id,
        schedule_info=get_schedule_info(
            get_schedule_hourly_or_less(args),
            args.time_to_live),
        enabled=args.enabled)

def modify_daily(conninfo, credentials, args):
    print snapshot.modify_policy(
        conninfo, credentials,
        args.id,
        name=args.name,
        source_file_id=args.file_id,
        schedule_info=get_schedule_info(
            get_schedule_daily(args),
            args.time_to_live),
        enabled=args.enabled)

def modify_monthly(conninfo, credentials, args):
    print snapshot.modify_policy(
        conninfo, credentials,
        args.id,
        name=args.name,
        source_file_id=args.file_id,
        schedule_info=get_schedule_info(
            get_schedule_monthly(args),
            args.time_to_live),
        enabled=args.enabled)

class ModifyPolicyCommand(qumulo.lib.opts.Subcommand):
    NAME = 'snapshot_modify_policy'

    DESCRIPTION = 'Modify an existing snapshot scheduling policy.'

    @staticmethod
    def options(parser):
        common_parser = argparse.ArgumentParser(add_help=False)

        common_parser.add_argument("-i", "--id", type=int, required=True,
            help="Identifier of the snapshot policy to modify.")
        common_parser.add_argument( '-n', '--name', type=str, default=None,
            help='Name of the policy.')
        common_parser.add_argument(
            '-t', '--time-to-live', type=str, default=None,
            help=POLICY_TTL_HELP)
        group = common_parser.add_mutually_exclusive_group(required=False)
        group.add_argument("--path", type=str, default=None,
            help="Path of directory upon which to take snapshots.")
        group.add_argument("--file-id", type=str, default=None,
            help="ID of directory upon which to take snapshots.")

        group = common_parser.add_mutually_exclusive_group(required=False)
        group.add_argument(
            '--enabled', dest='enabled', action='store_true',
            default=argparse.SUPPRESS,
            help='Enable the policy.')
        group.add_argument(
            '--disabled', dest='enabled', action='store_false',
            default=argparse.SUPPRESS,
            help='Disable the policy.')
        parser.set_defaults(enabled=None)

        subparsers = parser.add_subparsers()

        # Non schedule fields subparser
        modify_non_schedule_fields_parser = subparsers.add_parser(
            'modify_non_schedule_fields',
            parents=[common_parser],
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        modify_non_schedule_fields_parser.set_defaults(
            func=modify_non_schedule_fields)

        # Hourly or less subparser
        hourly_parser = subparsers.add_parser('change_to_hourly_or_less',
            parents=[common_parser, hourly_daily_common_parser],
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        add_hourly_specific_args(hourly_parser)
        add_general_schedule_args(hourly_parser)
        hourly_parser.set_defaults(func=modify_hourly)

        # Daily subparser
        daily_parser = subparsers.add_parser('change_to_daily',
            parents=[
                common_parser,
                hourly_daily_common_parser,
                daily_monthly_common_parser],
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        add_general_schedule_args(daily_parser)
        daily_parser.set_defaults(func=modify_daily)

        # Monthly subparser
        monthly_parser = subparsers.add_parser('change_to_monthly',
            parents=[common_parser, daily_monthly_common_parser],
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        add_monthly_specific_args(monthly_parser)
        add_general_schedule_args(monthly_parser)
        monthly_parser.set_defaults(func=modify_monthly)

    @staticmethod
    def main(conninfo, credentials, args):
        if args.path != None:
            attr = fs.get_attr(conninfo, credentials, args.path)
            args.file_id = attr.lookup('file_number')

        args.func(conninfo, credentials, args)

class ListAllPoliciesCommand(qumulo.lib.opts.Subcommand):
    NAME = 'snapshot_list_policies'

    DESCRIPTION = 'Lists all policies.'

    @staticmethod
    def main(conninfo, credentials, _args):
        print snapshot.list_policies(conninfo, credentials)

class GetPolicyCommand(qumulo.lib.opts.Subcommand):
    NAME = 'snapshot_get_policy'

    DESCRIPTION = 'Gets a single policy.'

    @staticmethod
    def options(parser):
        parser.add_argument("-i", "--id", type=int, required=True,
            help="Identifier of the snapshot policy to list.")

    @staticmethod
    def main(conninfo, credentials, args):
        print snapshot.get_policy(conninfo, credentials, args.id)

class DeletePolicyCommand(qumulo.lib.opts.Subcommand):
    NAME = 'snapshot_delete_policy'

    DESCRIPTION = 'Delete a single scheduling policy.'

    @staticmethod
    def options(parser):
        parser.add_argument("-i", "--id", type=int, required=True,
            help="Identifier of the snapshot policy to delete.")

    @staticmethod
    def main(conninfo, credentials, args):
        snapshot.delete_policy(conninfo, credentials, args.id)

class ListPolicyStatusesCommand(qumulo.lib.opts.Subcommand):
    NAME = 'snapshot_list_policy_statuses'

    DESCRIPTION = 'List all snapshot policy statuses.'

    @staticmethod
    def main(conninfo, credentials, _args):
        print snapshot.list_policy_statuses(conninfo, credentials)

class GetPolicyStatusCommand(qumulo.lib.opts.Subcommand):
    NAME = 'snapshot_get_policy_status'

    DESCRIPTION = 'Get a single snapshot policy status.'

    @staticmethod
    def options(parser):
        parser.add_argument("-i", "--id", type=int, required=True,
            help="Identifier of the snapshot policy.")

    @staticmethod
    def main(conninfo, credentials, args):
        print snapshot.get_policy_status(conninfo, credentials, args.id)

class GetSnapshotTotalUsedCapacity(qumulo.lib.opts.Subcommand):
    NAME = 'snapshot_get_total_used_capacity'

    DESCRIPTION = 'Get the total space consumed by all snapshots.'

    @staticmethod
    def main(conninfo, credentials, _args):
        print snapshot.get_total_used_capacity(conninfo, credentials)

class CalculateUsedCapacity(qumulo.lib.opts.Subcommand):
    NAME = 'snapshot_calculate_used_capacity'

    DESCRIPTION = 'Get the space used by the snapshots specified.'

    @staticmethod
    def options(parser):
        parser.add_argument('-i', '--ids', type=str,
            help='Identifiers of the snapshots for which to calculate '
                'capacity usage (as a comma separated list).')

    @staticmethod
    def main(conninfo, credentials, args):
        try:
            ids = [int(i) for i in args.ids.split(',')]
        except Exception:
            raise ValueError('Snapshot identifiers must be specified as ' \
                    'a comma separated list of positive integers.')
        print snapshot.calculate_used_capacity(conninfo, credentials, ids)

class GetUsedCapacityPerSnapshotCommand(qumulo.lib.opts.Subcommand):
    NAME = "snapshot_get_capacity_used_per_snapshot"

    DESCRIPTION = "Get the approximate amount of space for each snapshot that "\
                  "would be reclaimed if that snapshot were deleted."

    @staticmethod
    def options(parser):
        parser.add_argument("-i", "--id", type=int, required=False,
            help="If set, will return capacity usage of the snapshot with the "\
            "specified id. If omitted, will return capacity usage of all " \
            "snapshots.")

    @staticmethod
    def main(conninfo, credentials, args):
        if args.id is None:
            print snapshot.capacity_used_per_snapshot(conninfo, credentials)
        else:
            print snapshot.capacity_used_by_snapshot(
                conninfo, credentials, args.id)

class SnapshotTreeDiffCommand(qumulo.lib.opts.Subcommand):
    NAME = "snapshot_diff"

    DESCRIPTION = "List the changed files and directories between two "\
                  "snapshots."

    @staticmethod
    def options(parser):
        parser.add_argument(
            "--newer-snapshot",
            help="Snapshot ID of the newer snapshot",
            required=True,
            type=int)
        parser.add_argument(
            "--older-snapshot",
            help="Snapshot ID of the older snapshot",
            required=True,
            type=int)
        parser.add_argument(
            "--page-size",
            help="Max snapshot diff entries to return per request",
            type=int)

    @staticmethod
    def main(conninfo, credentials, args):
        for res in snapshot.get_all_snapshot_tree_diff(conninfo, credentials,
                args.newer_snapshot, args.older_snapshot, limit=args.page_size):
            print res

class SnapshotFileDiffCommand(qumulo.lib.opts.Subcommand):
    NAME = "snapshot_file_diff"

    DESCRIPTION = "List changed byte ranges of a file between two snapshots."

    @staticmethod
    def options(parser):
        parser.add_argument(
            "--newer-snapshot",
            help="Snapshot ID of the newer snapshot",
            required=True,
            type=int)
        parser.add_argument(
            "--older-snapshot",
            help="Snapshot ID of the older snapshot",
            required=True,
            type=int)
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to file", type=str)
        group.add_argument("--file-id", help="File ID", type=str)
        parser.add_argument(
            "--page-size",
            help="Maximum number of entries to return per request",
            type=int)

    @staticmethod
    def main(conninfo, credentials, args):
        for res in snapshot.get_all_snapshot_file_diff(
                conninfo, credentials,
                newer_snap=args.newer_snapshot, older_snap=args.older_snapshot,
                path=args.path, file_id=args.file_id, limit=args.page_size):
            print res
