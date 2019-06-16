# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2019 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Batch-related commands
"""

from __future__ import unicode_literals, absolute_import

import datetime
import logging

from rattail.commands.core import Subcommand, date_argument, dict_argument
from rattail.progress import SocketProgress
from rattail.time import localtime, make_utc


log = logging.getLogger(__name__)


class BatchHandlerCommand(Subcommand):
    """
    Base class for commands which invoke a batch handler.
    """

    def add_parser_args(self, parser):
        parser.add_argument('--batch-type', metavar='KEY',
                            help="Type of batch to be dealt with, e.g. 'vendor_catalog'")
        parser.add_argument('--dry-run', action='store_true',
                            help="Go through the full motions and allow logging etc. to "
                            "occur, but rollback (abort) the transaction at the end.")

    def get_handler(self, args):
        from rattail.batch import get_batch_handler

        handler = get_batch_handler(self.config, args.batch_type)
        assert handler
        return handler


class BatchAction(BatchHandlerCommand):
    """
    Base class for commands which invoke a handler to act on a single batch.
    """

    def add_parser_args(self, parser):
        super(BatchAction, self).add_parser_args(parser)
        parser.add_argument('batch_uuid',
                            help="UUID of the batch to be populated.")

    def run(self, args):
        handler = self.get_handler(args)
        session = self.make_session()
        user = self.get_runas_user(session)

        batch = session.query(handler.batch_model_class).get(args.batch_uuid)
        if not batch:
            raise RuntimeError("Batch of type '{}' not found: {}".format(args.batch_type, args.batch_uuid))

        success = self.action(args, handler, batch, user)

        if args.dry_run:
            session.rollback()
            log.info("dry run, so transaction was rolled back")
        elif success:
            session.commit()
            log.info("transaction was committed")
        else:
            session.rollback()
            log.warning("action failed, so transaction was rolled back")
        session.close()


class PopulateBatch(BatchAction):
    """
    Populate initial data for a batch
    """
    name = 'populate-batch'
    description = __doc__.strip()

    def action(self, args, handler, batch, user):
        return handler.do_populate(batch, user, progress=self.progress)


class RefreshBatch(BatchAction):
    """
    Refresh data for a batch
    """
    name = 'refresh-batch'
    description = __doc__.strip()

    def action(self, args, handler, batch, user):
        return handler.do_refresh(batch, user, progress=self.progress)


class ExecuteBatch(BatchAction):
    """
    Execute a batch
    """
    name = 'execute-batch'
    description = __doc__.strip()

    def add_parser_args(self, parser):
        super(ExecuteBatch, self).add_parser_args(parser)

        parser.add_argument('--kwargs', type=dict_argument, default={},
                            help="Optional JSON-encoded string containing extra "
                            "keyword arguments to be passed to the handler's batch "
                            "execution function.")

    def action(self, args, handler, batch, user):
        return handler.do_execute(batch, user, progress=self.progress, **args.kwargs)


class PurgeBatches(BatchHandlerCommand):
    """
    Purge old batches from the database
    """
    name = 'purge-batches'
    description = __doc__.strip()

    def add_parser_args(self, parser):
        super(PurgeBatches, self).add_parser_args(parser)

        parser.add_argument('--before', type=date_argument, metavar='DATE',
                            help="Purge all batches executed prior to this date.  If not "
                            "specified, will use --before-days to calculate instead.")

        parser.add_argument('--before-days', type=int, default=90, metavar='DAYS',
                            help="Number of days before the current date, to be used "
                            "as the cutoff date if --before is not specified.  Default "
                            "is 90 days before current date.")

        parser.add_argument('--list-types', action='store_true',
                            help="If set, list available batch types instead of trying "
                            "to purge anything.")


    def run(self, args):
        if args.list_types:
            self.list_types()
            return

        handler = self.get_handler(args)
        log.info("purging batches of type: %s", args.batch_type)
        session = self.make_session()

        kwargs = {
            'delete_all_data': not args.dry_run,
            'progress': self.progress,
        }
        if args.before:
            before = datetime.datetime.combine(args.before, datetime.time(0))
            before = localtime(self.config, before)
            kwargs['before'] = before
        else:
            kwargs['before_days'] = args.before_days

        purged = handler.purge_batches(session, **kwargs)
        log.info("%spurged %s batches", "(would have) " if args.dry_run else "", purged)

        if args.dry_run:
            session.rollback()
            log.info("dry run, so transaction was rolled back")
        else:
            session.commit()
            log.info("transaction was committed")
        session.close()

    def list_types(self):
        from rattail.batch.handlers import get_batch_types

        keys = get_batch_types(self.config)
        for key in keys:
            self.stdout.write("{}\n".format(key))
