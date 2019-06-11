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

import datetime
import textwrap

import qumulo.lib.auth
import qumulo.lib.opts
import qumulo.rest.replication as replication

from qumulo.lib.util import bool_from_string

DELETE_CONFIRMATION = (
    'This will delete the relationship without modifying the contents of '
    'the source or target directories. Note that there might be '
    'inconsistent (i.e. partially-replicated) data in the target directory '
    'if a job is currently running or if the previous job was '
    'incomplete.\n\n'
    'Proceed with deletion?')

class ReplicationReplicate(qumulo.lib.opts.Subcommand):
    NAME = "replication_replicate"
    DESCRIPTION = "Replicate from the source to the target of the " \
        "specified relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the source replication relationship")

    @staticmethod
    def main(conninfo, credentials, args):
        print replication.replicate(conninfo, credentials, args.id)

class ReplicationCreateSourceRelationship(qumulo.lib.opts.Subcommand):
    NAME = "replication_create_source_relationship"
    DESCRIPTION = "Create a new replication relationship."

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--source-id", type=str, help="File ID of the source directory")
        group.add_argument(
            "--source-path", type=str, help="Path to the source directory")

        parser.add_argument(
            "--target-path", required=True, help="Path to the target directory")
        parser.add_argument(
            "--target-address", required=True, help="The target IP address")
        parser.add_argument(
            "--target-port", type=int, required=False,
            help="Network port to replicate to on the target "
                "(overriding default)")

        parser.add_argument(
            "--enable-continuous-replication",
            type=bool_from_string,
            metavar='{true,false}',
            required=False)
        parser.add_argument(
            "--set-source-directory-read-only",
            type=bool_from_string,
            metavar='{true,false}',
            required=False)

    @staticmethod
    def main(conninfo, credentials, args):
        optional_args = {}
        if args.target_port is not None:
            optional_args['target_port'] = args.target_port

        if args.enable_continuous_replication is not None:
            optional_args['continuous_replication_enabled'] = \
                args.enable_continuous_replication

        if args.set_source_directory_read_only is not None:
            optional_args['source_root_read_only'] = \
                args.set_source_directory_read_only

        print replication.create_source_relationship(
            conninfo,
            credentials,
            args.target_path,
            args.target_address,
            source_id=args.source_id,
            source_path=args.source_path,
            **optional_args)

class ReplicationListSourceRelationships(qumulo.lib.opts.Subcommand):
    NAME = "replication_list_source_relationships"
    DESCRIPTION = "List existing source replication relationships."

    @staticmethod
    def main(conninfo, credentials, _args):
        print replication.list_source_relationships(conninfo, credentials)

class ReplicationGetSourceRelationship(qumulo.lib.opts.Subcommand):
    NAME = "replication_get_source_relationship"
    DESCRIPTION = "Get information about the specified " \
        "source replication relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the source replication relationship")

    @staticmethod
    def main(conninfo, credentials, args):
        print replication.get_source_relationship(
            conninfo, credentials, args.id)

class ReplicationDeleteSourceRelationship(qumulo.lib.opts.Subcommand):
    NAME = "replication_delete_source_relationship"
    DESCRIPTION = "Delete the specified source replication relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the source replication relationship")
        parser.add_argument(
            "--force", action="store_true", help="Do not prompt")

    @classmethod
    def _ask_confirmation(cls):
        return qumulo.lib.opts.ask(cls.NAME, DELETE_CONFIRMATION)

    @classmethod
    def main(cls, conninfo, credentials, args):
        if (args.force or cls._ask_confirmation()):
            replication.delete_source_relationship(
                conninfo, credentials, args.id)

class ReplicationModifySourceRelationship(qumulo.lib.opts.Subcommand):
    NAME = "replication_modify_source_relationship"
    DESCRIPTION = "Modify an existing source replication relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the source replication relationship")

        parser.add_argument(
            "--new-target-address", required=False,
            help="The target IP address")
        parser.add_argument(
            "--new-target-port", type=int, required=False,
            help="Network port to replicate to on the target")
        parser.add_argument('-z', '--timezone', type=str,
            help='The timezone for the relationship\'s blackout windows ' \
                '(e.g. America/Los_Angeles or UTC). See the ' \
                'time_list_timezones qq command for a complete list of ' \
                'supported timezones.')
        parser.add_argument(
            "--enable-continuous-replication",
            type=bool_from_string,
            metavar='{true,false}',
            required=False)
        parser.add_argument(
            "--set-source-directory-read-only",
            type=bool_from_string,
            metavar='{true,false}',
            required=False)

    @staticmethod
    def main(conninfo, credentials, args):
        optional_args = {}
        if args.new_target_address is not None:
            optional_args['new_target_address'] = args.new_target_address
        if args.new_target_port is not None:
            optional_args['new_target_port'] = args.new_target_port
        if args.timezone is not None:
            optional_args['blackout_window_timezone'] = args.timezone
        if args.enable_continuous_replication is not None:
            optional_args['continuous_replication_enabled'] = \
                args.enable_continuous_replication
        if args.set_source_directory_read_only is not None:
            optional_args['source_root_read_only'] = \
                args.set_source_directory_read_only

        print replication.modify_source_relationship(
            conninfo, credentials, args.id, **optional_args)

class ReplicationDeleteTargetRelationship(qumulo.lib.opts.Subcommand):
    NAME = "replication_delete_target_relationship"
    DESCRIPTION = "Delete the specified target replication relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the target replication relationship")
        parser.add_argument(
            "--force", action="store_true", help="Do not prompt")

    @classmethod
    def _ask_confirmation(cls):
        return qumulo.lib.opts.ask(cls.NAME, DELETE_CONFIRMATION)

    @classmethod
    def main(cls, conninfo, credentials, args):
        if (args.force or cls._ask_confirmation()):
            replication.delete_target_relationship(
                conninfo, credentials, args.id)

class ReplicationListSourceRelationshipStatuses(qumulo.lib.opts.Subcommand):
    NAME = "replication_list_source_relationship_statuses"
    DESCRIPTION = "List statuses for all existing source replication " \
        "relationships."

    @staticmethod
    def main(conninfo, credentials, _args):
        print replication.list_source_relationship_statuses(
            conninfo, credentials)

class ReplicationListTargetRelationshipStatuses(qumulo.lib.opts.Subcommand):
    NAME = "replication_list_target_relationship_statuses"
    DESCRIPTION = "List statuses for all existing target " \
        "replication relationships."

    @staticmethod
    def main(conninfo, credentials, _args):
        print replication.list_target_relationship_statuses(
            conninfo, credentials)

class ReplicationGetSourceRelationshipStatus(qumulo.lib.opts.Subcommand):
    NAME = "replication_get_source_relationship_status"
    DESCRIPTION = "Get current status of the specified " \
        "source replication relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the source replication relationship")

    @staticmethod
    def main(conninfo, credentials, args):
        print replication.get_source_relationship_status(
            conninfo,
            credentials,
            args.id)

class ReplicationGetTargetRelationshipStatus(qumulo.lib.opts.Subcommand):
    NAME = "replication_get_target_relationship_status"
    DESCRIPTION = "Get current target of the specified " \
        "source replication relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the target replication relationship")

    @staticmethod
    def main(conninfo, credentials, args):
        print replication.get_target_relationship_status(
            conninfo,
            credentials,
            args.id)

class ReplicationAuthorize(qumulo.lib.opts.Subcommand):
    NAME = "replication_authorize"
    DESCRIPTION = "Authorize the specified replication relationship, "+ \
        "establishing this cluster as the target of replication."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the target replication relationship")
        parser.add_argument("--allow-non-empty-directory", action="store_true",
            help="Allow the replication relationship to be authorized on a " \
                "target directory containing existing data. Existing data in " \
                "the target directory may be deleted or overwritten. If you " \
                "wish to preserve this data, consider taking a snapshot" \
                " before authorizing.")
        parser.add_argument("--allow-fs-path-create", action="store_true",
            help="Allow the target directory to be created with " \
                "inherited permissions if it does not already exist")

    @staticmethod
    def main(conninfo, credentials, args):
        print replication.authorize(
            conninfo,
            credentials,
            args.id,
            allow_non_empty_directory=args.allow_non_empty_directory,
            allow_fs_path_create=args.allow_fs_path_create)

class ReplicationReconnectTargetRelationship(qumulo.lib.opts.Subcommand):
    NAME = "replication_reconnect_target_relationship"
    DESCRIPTION = "Reconnect the specified target replication relationship, " \
        "reestablishing the relationship with the source directory. The " \
        "target directory will be made read-only and any changes made to the " \
        "target directory since the relationship was disconnected will be " \
        "reverted."
    CONFIRMATION = DESCRIPTION + "\n\nData not present on the source will be " \
        "deleted. Do you want to proceed?"

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the target replication relationship")
        parser.add_argument("--force", action="store_true",
            help="Do not prompt")

    @staticmethod
    def main(conninfo, credentials, args):
        if args.force or qumulo.lib.opts.ask(
                ReplicationReconnectTargetRelationship.NAME,
                ReplicationReconnectTargetRelationship.CONFIRMATION):
            print replication.reconnect_target_relationship(
                conninfo, credentials, args.id)

class ReplicationAbortReplication(qumulo.lib.opts.Subcommand):
    NAME = "replication_abort_replication"
    DESCRIPTION = "Abort ongoing replication work for the specified " \
        "source replication relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the source replication relationship")

    @staticmethod
    def main(conninfo, credentials, args):
        replication.abort_replication(conninfo, credentials, args.id)

ALLOWED_DAYS = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT", "ALL"]

def get_on_days(days_of_week):
    days = [day.strip().upper() for day in days_of_week.split(",")]

    if "ALL" in days:
        if len(days) > 1:
            raise ValueError(
                "ALL cannot be used in conjunction with other days")

        # API parlance for "ALL"
        return ["EVERY_DAY"]

    if not set(days).issubset(set(ALLOWED_DAYS)):
        raise ValueError(
            "Invalid days: {}; allowed days are: {}".format(days, ALLOWED_DAYS))

    return days

def get_blackout_window(args):
    try:
        start_time = datetime.datetime.strptime(args.start_time, "%H:%M")
        end_time = datetime.datetime.strptime(args.end_time, "%H:%M")
    except ValueError:
        raise ValueError("Bad format for start/end time")

    return {
        "start_hour": start_time.hour,
        "start_minute": start_time.minute,
        "end_hour": end_time.hour,
        "end_minute": end_time.minute,
        "on_days": get_on_days(args.days_of_week),
    }

class ReplicationAddBlackoutWindow(qumulo.lib.opts.Subcommand):
    NAME = "replication_add_blackout_window"
    DESCRIPTION = "Add a blackout window to the specified source replication " \
        "relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the source replication relationship.")

        parser.add_argument("--start-time", required=True, type=str,
            help="The 24 hour time of day start time for the blackout " \
                "window (e.g 15:30).")

        parser.add_argument("--end-time", required=True, type=str,
            help="The 24 hour time of day end time for the blackout " \
                "window (e.g 18:30) -- on the following day if earlier than " \
                "the --start-time parameter.")

        parser.add_argument("--days-of-week", required=True, type=str,
            help="Days of the week the window applies to. Comma separated " \
                "list (e.g. MON,TUE,WED,THU,FRI,SAT,SUN,ALL).")

    @staticmethod
    def main(conninfo, credentials, args):
        relationship, etag = \
            replication.get_source_relationship(conninfo, credentials, args.id)

        blackout_windows = relationship['blackout_windows']

        blackout_windows.append(get_blackout_window(args))

        print replication.modify_source_relationship(
            conninfo,
            credentials,
            args.id,
            blackout_windows=blackout_windows,
            etag=etag)

class ReplicationDeleteBlackoutWindows(qumulo.lib.opts.Subcommand):
    NAME = "replication_delete_blackout_windows"
    DESCRIPTION = "Delete blackout windows of the specified source " \
        "replication relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the source replication relationship")

    @staticmethod
    def main(conninfo, credentials, args):
        _, etag = \
            replication.get_source_relationship(conninfo, credentials, args.id)

        print replication.modify_source_relationship(
            conninfo, credentials, args.id, blackout_windows=[], etag=etag)

def format_timestamp(timestamp):
    '''
    Parse the ISO 8601 timestamp and return a string formatted according to the
    locale.
    '''
    # Remove the fractional seconds & timezone information from timestamp.
    # strptime can't parse ISO-8601 dates with nanoseconds.
    t = timestamp[:len('2019-02-06T19:21:53')]
    return datetime.datetime.\
        strptime(t, '%Y-%m-%dT%H:%M:%S').strftime('%b %d %Y, %I:%M %p')

class ReplicationMakeTargetWritable(qumulo.lib.opts.Subcommand):
    NAME = "replication_make_target_writable"
    DESCRIPTION = (
        'Revert target directory to the latest recovery point to ensure that '
        'it is in a point-in-time consistent state.  Then disconnect the '
        'specified target replication relationship, breaking the relationship '
        'with the source and making the target directory writable. The revert '
        'action may take some time to complete. If the relationship is later '
        'reconnected, any changes made to the target directory since the '
        'relationship was disconnected will be reverted upon reconnecting.')

    @staticmethod
    def options(parser):
        parser.add_argument(
            "--id",
            required=True,
            help="Unique identifier of the target replication relationship")
        parser.add_argument(
            "--force",
            action="store_true",
            help="Do not prompt")

    CONFIRMATION_TEMPLATE = (
        'This action will revert the target directory to the latest recovery '
        'point to ensure that it is in a point-in-time consistent state. '
        'Then, it will disconnect the replication relationship, making the '
        'target directory writable. The revert action may take some time to '
        'complete.\n\n'
        'This action will revert the target directory of {root} to the '
        'recovery point from {timestamp} UTC. Do you want to proceed?')

    NO_RECOVERY_POINT_TEMPLATE = (
        'Target directory {root} cannot be made writable because initial '
        'replication has not completed. If you would like to make the target '
        'directory writable, you will need to delete the replication '
        'relationship. Deleting the replication relationship can leave '
        'partially-replicated data in an inconsistent state.')

    @classmethod
    def _ask_confirmation(cls, conninfo, credentials, relationship_id):
        status = replication.get_target_relationship_status(
            conninfo, credentials, relationship_id).data
        root = status['target_root_path']
        timestamp = status['recovery_point']
        if not timestamp:
            print '\n'.join(textwrap.fill(line) for line in
                cls.NO_RECOVERY_POINT_TEMPLATE.format(root=root).splitlines())
            return False
        else:
            confirmation = cls.CONFIRMATION_TEMPLATE.format(
                root=root, timestamp=format_timestamp(timestamp))
        return qumulo.lib.opts.ask(cls.NAME, confirmation)

    @classmethod
    def main(cls, conninfo, credentials, args):
        if (args.force or
                cls._ask_confirmation(conninfo, credentials, args.id)):
            print replication.make_target_writable(
                conninfo, credentials, args.id)

class ReplicationReverseTargetRelationship(qumulo.lib.opts.Subcommand):
    NAME = "replication_reverse_target_relationship"
    DESCRIPTION = (
        "Reverse source and target for the specified replication relationship. "
        "This operation is initiated on the target cluster. The previous "
        "target directory will be made the new source, and the previous source "
        "directory will be made the new target. After reversal completes, "
        "blackout windows will be reset and the relationship will remain "
        "disconnected, where replication will not resume. To resume "
        "replication after reversal, configure blackout windows from the new "
        "source cluster and reconnect the relationship from the new target "
        "cluster.")

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the target replication relationship")
        parser.add_argument("--source-address", required=True,
            help="The IP address of the current source cluster")
        parser.add_argument("--source-port", type=int, required=False,
            help=("Network port of the current source cluster (defaults to "
                "3712)"))

    @classmethod
    def main(cls, conninfo, credentials, args):
        optional_args = {}
        if args.source_port:
            optional_args['source_port'] = args.source_port
        print replication.reverse_target_relationship(conninfo, credentials,
            args.id, args.source_address, **optional_args)
