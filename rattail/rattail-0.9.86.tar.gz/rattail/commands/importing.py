# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
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
Importing Commands
"""

from __future__ import unicode_literals, absolute_import

import sys
import logging

import six

from rattail.commands.core import Subcommand, date_argument
from rattail.config import parse_list
from rattail.util import load_object


log = logging.getLogger(__name__)


class ImportSubcommand(Subcommand):
    """
    Base class for subcommands which use the (new) data importing system.
    """
    handler_spec = None

    # TODO: move this into Subcommand or something..
    parent_name = None
    def __init__(self, *args, **kwargs):
        if 'handler_spec' in kwargs:
            self.handler_spec = kwargs.pop('handler_spec')
        super(ImportSubcommand, self).__init__(*args, **kwargs)
        if self.parent:
            self.parent_name = self.parent.name

    def get_handler_factory(self, **kwargs):
        """
        Subclasses must override this, and return a callable that creates an
        import handler instance which the command should use.
        """
        if self.handler_spec:
            return load_object(self.handler_spec)
        raise NotImplementedError

    def get_handler(self, **kwargs):
        """
        Returns a handler instance to be used by the command.
        """
        factory = self.get_handler_factory(args=kwargs.get('args'))
        kwargs.setdefault('config', getattr(self, 'config', None))
        kwargs.setdefault('command', self)
        kwargs.setdefault('progress', self.progress)
        user = self.get_runas_user()
        if user:
            kwargs.setdefault('runas_user', user)
            kwargs.setdefault('runas_username', user.username)
        if 'args' in kwargs:
            args = kwargs['args']
            kwargs.setdefault('dry_run', args.dry_run)
            if hasattr(args, 'batch_size'):
                kwargs.setdefault('batch_size', args.batch_size)
            if args.max_diffs:
                kwargs.setdefault('diff_max_display', args.max_diffs)
            # kwargs.setdefault('max_create', args.max_create)
            # kwargs.setdefault('max_update', args.max_update)
            # kwargs.setdefault('max_delete', args.max_delete)
            # kwargs.setdefault('max_total', args.max_total)
        kwargs = self.get_handler_kwargs(**kwargs)
        return factory(**kwargs)

    def get_handler_kwargs(self, **kwargs):
        """
        Return a dict of kwargs to be passed to the handler factory.
        """
        return kwargs

    def add_parser_args(self, parser):

        # model names (aka importer keys)
        doc = ("Which data models to import.  If you specify any, then only "
               "data for those models will be imported.  If you do not specify "
               "any, then all *default* models will be imported.")
        try:
            handler = self.get_handler()
        except NotImplementedError:
            pass
        else:
            doc += "  Supported models are: ({})".format(', '.join(handler.get_importer_keys()))
        parser.add_argument('models', nargs='*', metavar='MODEL', help=doc)

        # make batches
        parser.add_argument('--make-batches', action='store_true',
                            help="If specified, make new Import / Export Batches instead of "
                            "performing an actual (possibly dry-run) import.")

        # key / fields / exclude
        parser.add_argument('--key', metavar='FIELDS',
                            help="List of fields which should be used as \"primary key\" for the import.")
        parser.add_argument('--fields',
                            help="List of fields which should be included in the import.  "
                            "If this parameter is specified, then any field not listed here, "
                            "would be *excluded* regardless of the --exclude-field parameter.")
        parser.add_argument('--exclude-fields',
                            help="List of fields which should be excluded from the import.  "
                            "Any field not listed here, would be included (or not) depending "
                            "on the --fields parameter and/or default importer behavior.")

        # date ranges
        parser.add_argument('--start-date', type=date_argument, metavar='DATE',
                            help="Optional (inclusive) starting point for date range, by which host "
                            "data should be filtered.  Only used by certain importers.")
        parser.add_argument('--end-date', type=date_argument, metavar='DATE',
                            help="Optional (inclusive) ending point for date range, by which host "
                            "data should be filtered.  Only used by certain importers.")
        parser.add_argument('--year', type=int,
                            help="Optional year, by which data should be filtered.  Only used "
                            "by certain importers.")

        # allow create?
        parser.add_argument('--create', action='store_true', default=True,
                            help="Allow new records to be created during the import.")
        parser.add_argument('--no-create', action='store_false', dest='create',
                            help="Do not allow new records to be created during the import.")
        parser.add_argument('--max-create', type=int, metavar='COUNT',
                            help="Maximum number of records which may be created, after which a "
                            "given import task should stop.  Note that this applies on a per-model "
                            "basis and not overall.")

        # allow update?
        parser.add_argument('--update', action='store_true', default=True,
                            help="Allow existing records to be updated during the import.")
        parser.add_argument('--no-update', action='store_false', dest='update',
                            help="Do not allow existing records to be updated during the import.")
        parser.add_argument('--max-update', type=int, metavar='COUNT',
                            help="Maximum number of records which may be updated, after which a "
                            "given import task should stop.  Note that this applies on a per-model "
                            "basis and not overall.")

        # allow delete?
        parser.add_argument('--delete', action='store_true', default=False,
                            help="Allow records to be deleted during the import.")
        parser.add_argument('--no-delete', action='store_false', dest='delete',
                            help="Do not allow records to be deleted during the import.")
        parser.add_argument('--max-delete', type=int, metavar='COUNT',
                            help="Maximum number of records which may be deleted, after which a "
                            "given import task should stop.  Note that this applies on a per-model "
                            "basis and not overall.")

        # max total changes, per model
        parser.add_argument('--max-total', type=int, metavar='COUNT',
                            help="Maximum number of *any* record changes which may occur, after which "
                            "a given import task should stop.  Note that this applies on a per-model "
                            "basis and not overall.")

        # TODO: deprecate --batch, replace with --batch-size ?
        # batch size
        parser.add_argument('--batch', type=int, dest='batch_size', metavar='SIZE', default=200,
                            help="Split work to be done into batches, with the specified number of "
                            "records in each batch.  Or, set this to 0 (zero) to disable batching. "
                            "Implementation for this may vary somewhat between importers; default "
                            "batch size is 200 records.")

        # treat changes as warnings?
        parser.add_argument('--warnings', '-W', action='store_true',
                            help="Set this flag if you expect a \"clean\" import, and wish for any "
                            "changes which do occur to be processed further and/or specially.  The "
                            "behavior of this flag is ultimately up to the import handler, but the "
                            "default is to send an email notification.")

        # max diffs per warning type
        parser.add_argument('--max-diffs', type=int, metavar='COUNT',
                            help="Maximum number of \"diffs\" to display per warning type, in a "
                            "warning email.  Only used if --warnings is in effect.")

        # dry run?
        parser.add_argument('--dry-run', action='store_true',
                            help="Go through the full motions and allow logging etc. to "
                            "occur, but rollback (abort) the transaction at the end.  "
                            "Note that this flag is ignored if --make-batches is specified.")

    def run(self, args):
        log.info("begin `%s %s` for data models: %s",
                 self.parent_name,
                 self.name,
                 ', '.join(args.models) if args.models else "(ALL)")

        handler = self.get_handler(args=args)
        models = args.models or handler.get_default_keys()
        log.debug("using handler: {}".format(handler))
        log.debug("importing models: {}".format(models))
        log.debug("args are: {}".format(args))

        kwargs = {
            'warnings': args.warnings,
            'fields': parse_list(args.fields),
            'exclude_fields': parse_list(args.exclude_fields),
            'create': args.create,
            'max_create': args.max_create,
            'update': args.update,
            'max_update': args.max_update,
            'delete': args.delete,
            'max_delete': args.max_delete,
            'max_total': args.max_total,
            'progress': self.progress,
            'args': args,
        }
        if args.make_batches:
            kwargs.update({
                'runas_user': self.get_runas_user(),
            })
            handler.make_batches(*models, **kwargs)
        else:
            kwargs.update({
                'key_fields': parse_list(args.key) if args.key else None,
                'dry_run': args.dry_run,
            })
            handler.import_data(*models, **kwargs)

        # TODO: should this logging happen elsewhere / be customizable?
        if args.dry_run:
            log.info("dry run, so transaction was rolled back")
        else:
            log.info("transaction was committed")


class ImportFromCSV(ImportSubcommand):
    """
    Generic base class for commands which import from a CSV file.
    """

    def add_parser_args(self, parser):
        super(ImportFromCSV, self).add_parser_args(parser)

        parser.add_argument('--source-csv', metavar='PATH', required=True,
                            help="Path to CSV file to be used as data source.")


class ExportRattail(ImportSubcommand):
    """
    Export data to another Rattail database
    """
    name = 'export-rattail'
    description = __doc__.strip()
    default_handler_spec = 'rattail.importing.rattail:FromRattailToRattailExport'
    default_dbkey = 'host'

    def get_handler_factory(self, **kwargs):
        if self.config:
            spec = self.config.get('rattail.exporting', 'rattail.handler',
                                   default=self.default_handler_spec)
        else:
            # just use default, for sake of cmd line help
            spec = self.default_handler_spec
        return load_object(spec)

    def add_parser_args(self, parser):
        super(ExportRattail, self).add_parser_args(parser)
        parser.add_argument('--dbkey', metavar='KEY', default=self.default_dbkey,
                            help="Config key for database engine to be used as the \"target\" "
                            "Rattail system, i.e. where data will be exported.  This key must "
                            "be defined in the [rattail.db] section of your config file.")

    def get_handler_kwargs(self, **kwargs):
        if 'args' in kwargs:
            kwargs['dbkey'] = kwargs['args'].dbkey
        return kwargs


class ImportToRattail(ImportSubcommand):
    """
    Generic base class for commands which import *to* a Rattail system.
    """
    # subclass must set these!
    handler_key = None
    default_handler_spec = None

    def get_handler_factory(self, **kwargs):
        if self.config:
            spec = self.config.get('rattail.importing', '{}.handler'.format(self.handler_key),
                                   default=self.default_handler_spec)
        else:
            # just use default, for sake of cmd line help
            spec = self.default_handler_spec
        return load_object(spec)


class ImportRattail(ImportToRattail):
    """
    Import data from another Rattail database
    """
    name = 'import-rattail'
    description = __doc__.strip()
    handler_key = 'rattail'
    default_handler_spec = 'rattail.importing.rattail:FromRattailToRattailImport'
    accepts_dbkey_param = True

    def add_parser_args(self, parser):
        super(ImportRattail, self).add_parser_args(parser)
        if self.accepts_dbkey_param:
            parser.add_argument('--dbkey', metavar='KEY', default='host',
                                help="Config key for database engine to be used as the Rattail "
                                "\"host\", i.e. the source of the data to be imported.  This key "
                                "must be defined in the [rattail.db] section of your config file.  "
                                "Defaults to 'host'.")

    def get_handler_kwargs(self, **kwargs):
        if self.accepts_dbkey_param:
            if 'args' in kwargs:
                kwargs['dbkey'] = kwargs['args'].dbkey
        return kwargs


class ImportRattailBulk(ImportRattail):
    """
    Bulk-import data from another Rattail database
    """
    name = 'import-rattail-bulk'
    description = __doc__.strip()
    handler_key = 'rattail_bulk'
    default_handler_spec = 'rattail.importing.rattail_bulk:BulkFromRattailToRattail'


class ImportSampleData(ImportToRattail):
    """
    Import sample data to a Rattail database
    """
    name = 'import-sample'
    description = __doc__.strip()
    handler_key = 'sample'
    default_handler_spec = 'rattail.importing.sample:FromSampleToRattail'


class ImportVersions(ImportRattail):
    """
    Make initial versioned records for data models
    """
    name = 'import-versions'
    description = __doc__.strip()
    handler_key = 'versions'
    default_handler_spec = 'rattail.importing.versions:FromRattailToRattailVersions'
    accepts_dbkey_param = False
    default_comment = "import catch-up versions"

    def add_parser_args(self, parser):
        super(ImportVersions, self).add_parser_args(parser)
        parser.add_argument('--comment', type=six.text_type, default=self.default_comment,
                            help="Comment to be recorded with the transaction.  "
                            "Default is \"{}\".".format(self.default_comment))

    def get_handler_kwargs(self, **kwargs):
        if 'args' in kwargs:
            kwargs['comment'] = kwargs['args'].comment
        return kwargs

    def run(self, args):
        if not self.config.versioning_enabled():
            self.stderr.write("Continuum versioning is not enabled, per config\n")
            sys.exit(1)
        super(ImportVersions, self).run(args)
