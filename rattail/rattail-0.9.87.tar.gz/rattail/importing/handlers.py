# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2018 Lance Edgar
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
Import Handlers
"""

from __future__ import unicode_literals, absolute_import

import sys
import logging

import six
import humanize
import sqlalchemy as sa

from rattail.core import get_uuid
from rattail.time import make_utc
from rattail.util import OrderedDict, get_object_spec, progress_loop
from rattail.mail import send_email


log = logging.getLogger(__name__)


class ImportHandler(object):
    """
    Base class for all import handlers.

    .. attribute:: direction

       Should be a string, either ``'import'`` or ``'export'``.  This value is
       used to improve verbiage for logging and other output, for a better
       overall user experience.  It may also be used by importer logic, where
       the direction would otherwise be ambiguous.

       For "most" handlers the distinction is somewhat implied, e.g. Rattail ->
       POS is almost certainly thought of as an *export*, whereas POS ->
       Rattail would be an *import*.  However "export" handlers should still
       define this value accordingly; it's optional for "import" since that is
       the default.

       The value is most useful though, where it is otherwise ambiguous.
       Within a Rattail -> Rattail handler for instance, importer logic may
       consult this value in order to do different things depending on which
       "side" is the local "default" DB.  For example you may have a "host" and
       multiple "store" nodes, and you want to "push" some tables from host ->
       store, but not the other way around.  Since presumably *both* of the
       ``rattail import-rattail`` and ``rattail export-rattail`` (i.e. pull and
       push) commands should be valid to run from any given node, and since the
       importers themselves are "direction-agnostic", the importers must
       consult :attr:`~rattail.importing.importers.Importer.direction` (as well
       as :meth:`~rattail.config.RattailConfig.node_type()`) to know which
       tables to support for each command run.
    """
    host_title = None
    local_title = None
    progress = None
    dry_run = False
    commit_host_partial = False
    diff_max_display = 15
    direction = 'import'

    def __init__(self, config=None, **kwargs):
        self.config = config
        self.enum = config.get_enum() if config else None
        self.importers = self.get_importers()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_importers(self):
        """
        Returns a dict of all available importers, where the keys are model
        names and the values are importer factories.  All subclasses will want
        to override this.  Note that if you return an
        :class:`python:collections.OrderedDict` instance, you can affect the
        ordering of keys in the command line help system, etc.
        """
        return {}

    def get_importer_keys(self):
        """
        Returns the list of keys corresponding to the available importers.
        """
        return list(self.importers.keys())

    def get_default_keys(self):
        """
        Returns the list of keys corresponding to the "default" importers.
        Override this if you wish certain importers to be excluded by default,
        e.g. when first testing them out etc.
        """
        return self.get_importer_keys()

    def get_importer(self, key, **kwargs):
        """
        Returns an importer instance corresponding to the given key.
        """
        if key in self.importers:
            kwargs.setdefault('handler', self)
            kwargs.setdefault('config', self.config)
            kwargs.setdefault('host_system_title', self.host_title)
            kwargs.setdefault('direction', self.direction)
            if hasattr(self, 'batch_size'):
                kwargs.setdefault('batch_size', self.batch_size)
            kwargs = self.get_importer_kwargs(key, **kwargs)
            kwargs['key'] = kwargs.pop('key_fields', None)
            return self.importers[key](**kwargs)

    def get_importer_kwargs(self, key, **kwargs):
        """
        Return a dict of kwargs to be used when construcing an importer with
        the given key.
        """
        return kwargs

    def make_batches(self, *keys, **kwargs):
        """
        Make new import/export batch for each specified model key.
        """
        from rattail.db import Session

        session = Session()
        model = self.config.get_model()
        metadata = sa.MetaData(schema='batch', bind=session.bind)
        user = session.merge(kwargs['runas_user'])
        handler_spec = self.config.get('rattail.batch', 'importer.handler',
                                       default='rattail.batch.importer:ImporterBatchHandler')

        self.progress = kwargs.pop('progress', getattr(self, 'progress', None))

        self.setup()
        self.begin_transaction()
        batches = []

        for key in keys:

            importer = self.get_importer(key, **kwargs)
            if importer and importer.batches_supported:
                log.info("making batch for model: %s", key)
                importer._handler_key = key

                batch = model.ImporterBatch()
                batch.uuid = get_uuid()
                batch.created_by = user
                batch.batch_handler_spec = handler_spec
                batch.import_handler_spec = get_object_spec(self)
                batch.host_title = self.host_title
                batch.local_title = self.local_title
                batch.importer_key = key
                batch.rowcount = 0

                batch.description = "{} -> {} for {}".format(
                    batch.host_title,
                    batch.local_title,
                    batch.importer_key)

                batch.row_table = batch.uuid

                session.add(batch)
                session.flush()

                row_table = self.make_row_table(metadata, importer, batch)
                self.populate_row_table(session, importer, batch, row_table)
                batches.append(batch)

            elif importer:
                log.info("batches not supported for importer: %s", key)

            else:
                log.warning("skipping unknown model: %s", key)

        self.teardown()
        # TODO: necessary?
        # self.rollback_transaction()
        # self.commit_transaction()

        session.commit()
        session.close()
        return batches

    def make_row_table(self, metadata, importer, batch):
        columns = [
            sa.Column('uuid', sa.String(length=32), nullable=False, primary_key=True),
            sa.Column('sequence', sa.Integer(), nullable=False),
            sa.Column('object_key', sa.String(length=255), nullable=False, default=''),
            sa.Column('object_str', sa.String(length=255), nullable=False, default=''),
        ]

        for field in importer.fields:
            typ = importer.field_coltypes.get(field)

            if not typ and importer.model_class:
                mapper = sa.inspect(importer.model_class)
                if mapper.has_property(field):
                    prop = mapper.get_property(field)
                    if prop:
                        assert len(prop.columns) == 1, "multiple columns ({}) unsupported: {}.{}".format(
                            len(prop.columns), batch.importer_key, field)
                        typ = prop.columns[0].type

            if not typ:
                typ = sa.String(length=255)

            if field in importer.key:
                columns.append(sa.Column('key_{}'.format(field), typ))
            else:
                for prefix in ('pre', 'post'):
                    columns.append(sa.Column('{}_{}'.format(prefix, field), typ))

        columns.extend([
            sa.Column('status_code', sa.Integer(), nullable=False),
            sa.Column('status_text', sa.String(length=255), nullable=True),
        ])

        row_table = sa.Table(batch.row_table, metadata, *columns)
        row_table.create()
        return row_table

    def populate_row_table(self, session, importer, batch, row_table):
        importer.now = make_utc(tzinfo=True)
        importer.setup()

        # obtain host data
        host_data = importer.normalize_host_data()
        host_data, unique = importer.unique_data(host_data)
        if not host_data:
            return

        # cache local data if appropriate
        if importer.caches_local_data:
            importer.cached_local_data = importer.cache_local_data(host_data)

        # create and/or update
        if importer.create or importer.update:
            self._populate_create_update(session, importer, batch, row_table, host_data)

        # delete
        if importer.delete:
            self._populate_delete(session, importer, batch, row_table, host_data, set(unique))

    def _populate_delete(self, session, importer, batch, row_table, host_data, host_keys):
        deleting = importer.get_deletion_keys() - host_keys

        def delete(key, i):
            cached = importer.cached_local_data.pop(key)
            local_data = cached['data']
            local_data['_object_str'] = six.text_type(cached['object'])
            sequence = batch.rowcount + 1
            self.make_batch_row(session, importer, row_table, sequence, None, local_data,
                                status_code=self.enum.IMPORTER_BATCH_ROW_STATUS_DELETE)
            batch.rowcount += 1

        progress_loop(delete, sorted(deleting), self.progress,
                      message="Deleting {} data".format(importer.model_name))

    def _populate_create_update(self, session, importer, batch, row_table, data):

        def record(host_data, i):

            # fetch local object, using key from host data
            key = importer.get_key(host_data)
            local_object = importer.get_local_object(key)
            status_code = self.enum.IMPORTER_BATCH_ROW_STATUS_NOCHANGE
            status_text = None
            make_row = False

            # if we have a local object, but its data differs from host, make an update record
            if local_object and importer.update:
                make_row = True
                local_data = importer.normalize_local_object(local_object)
                diffs = importer.data_diffs(local_data, host_data)
                if diffs:
                    status_code = self.enum.IMPORTER_BATCH_ROW_STATUS_UPDATE
                    status_text = ','.join(diffs)

            # if we did not yet have a local object, make a create record
            elif not local_object and importer.create:
                make_row = True
                local_data = None
                status_code = self.enum.IMPORTER_BATCH_ROW_STATUS_CREATE

            if make_row:
                sequence = batch.rowcount + 1
                self.make_batch_row(session, importer, row_table, sequence, host_data, local_data,
                                    status_code=status_code, status_text=status_text)
                batch.rowcount += 1

        progress_loop(record, data, self.progress,
                      message="Populating batch for {}".format(importer._handler_key))

    def make_batch_row(self, session, importer, row_table, sequence, host_data, local_data, status_code=None, status_text=None):
        values = {
            'uuid': get_uuid(),
            'sequence': sequence,
            'object_str': '',
            'status_code': status_code,
            'status_text': status_text,
        }

        if host_data:
            if '_object_str' in host_data:
                values['object_str'] = host_data['_object_str']
            elif '_host_object' in host_data:
                values['object_str'] = six.text_type(host_data['_host_object'])
            values['object_key'] = ','.join([six.text_type(host_data[f]) for f in importer.key])
        elif local_data:
            if '_object_str' in local_data:
                values['object_str'] = local_data['_object_str']
            elif '_object' in local_data:
                values['object_str'] = six.text_type(local_data['_object'])
            values['object_key'] = ','.join([local_data[f] for f in importer.key])

        for field in importer.fields:
            if field in importer.key:
                data = host_data or local_data
                values['key_{}'.format(field)] = data[field]
            else:
                if host_data and field in host_data:
                    values['post_{}'.format(field)] = host_data[field]
                if local_data and field in local_data:
                    values['pre_{}'.format(field)] = local_data[field]

        session.execute(row_table.insert(values))

    def import_data(self, *keys, **kwargs):
        """
        Import all data for the given importer/model keys.
        """
        self.import_began = make_utc(tzinfo=True)
        if 'dry_run' in kwargs:
            self.dry_run = kwargs['dry_run']
        self.progress = kwargs.pop('progress', getattr(self, 'progress', None))
        self.warnings = kwargs.get('warnings', False)
        kwargs.update({'dry_run': self.dry_run,
                       'progress': self.progress})

        self.setup()
        self.begin_transaction()
        changes = OrderedDict()

        try:
            for key in keys:
                importer = self.get_importer(key, **kwargs)
                if importer:
                    created, updated, deleted = importer.import_data()
                    changed = bool(created or updated or deleted)
                    msg = "{} -> {}: added {:,d}; updated {:,d}; deleted {:,d} {} records"
                    if self.dry_run:
                        msg += " (dry run)"
                    logger = log.warning if changed and self.warnings else log.info
                    logger(msg.format(
                        self.host_title, self.local_title, len(created), len(updated), len(deleted), key))
                    if changed:
                        changes[key] = created, updated, deleted
                else:
                    log.warning("skipping unknown importer: {}".format(key))
        except:
            if self.commit_host_partial and not self.dry_run:
                log.warning("{host} -> {local}: committing partial transaction on host {host} (despite error)".format(
                    host=self.host_title, local=self.local_title))
                self.commit_host_transaction()
            raise
        else:
            if changes:
                self.process_changes(changes)
            if self.dry_run:
                self.rollback_transaction()
            else:
                self.commit_transaction()

        self.teardown()
        return changes

    def setup(self):
        """
        Perform any additional setup if/as necessary, prior to running the
        import task(s).
        """

    def teardown(self):
        """
        Perform any cleanup necessary, after running the import task(s).
        """

    def begin_transaction(self):
        self.begin_host_transaction()
        self.begin_local_transaction()

    def begin_host_transaction(self):
        pass

    def begin_local_transaction(self):
        pass

    def rollback_transaction(self):
        self.rollback_host_transaction()
        self.rollback_local_transaction()

    def rollback_host_transaction(self):
        pass

    def rollback_local_transaction(self):
        pass

    def commit_transaction(self):
        self.commit_host_transaction()
        self.commit_local_transaction()

    def commit_host_transaction(self):
        pass

    def commit_local_transaction(self):
        pass

    def process_changes(self, changes):
        """
        This method is called any time changes occur, regardless of whether the
        import is running in "warnings" mode.  Default implementation does
        nothing; override as needed.
        """
        # TODO: This whole thing needs a re-write...but for now, waiting until
        # the old importer has really gone away, so we can share its email
        # template instead of bothering with something more complicated.

        if not self.warnings:
            return

        now = make_utc(tzinfo=True)
        data = {
            'local_title': self.local_title,
            'host_title': self.host_title,
            'argv': sys.argv,
            'runtime': humanize.naturaldelta(now - self.import_began),
            'changes': changes,
            'dry_run': self.dry_run,
            'render_record': RecordRenderer(self.config),
            'max_display': self.diff_max_display,
        }

        command = getattr(self, 'command', None)
        if command:
            data['command'] = '{} {}'.format(command.parent.name, command.name)
        else:
            data['command'] = None

        if command:
            key = '{}_{}_updates'.format(command.parent.name, command.name)
            key = key.replace('-', '_')
        else:
            key = 'rattail_import_updates'

        send_email(self.config, key, fallback_key='rattail_import_updates', data=data)
        log.info("{} -> {}: warning email was sent".format(self.host_title, self.local_title))


class BulkImportHandler(ImportHandler):
    """
    Base class for bulk import handlers.
    """

    def import_data(self, *keys, **kwargs):
        """
        Import all data for the given importer/model keys.
        """
        # TODO: still need to refactor much of this so can share with parent class
        self.import_began = make_utc(tzinfo=True)
        if 'dry_run' in kwargs:
            self.dry_run = kwargs['dry_run']
        self.progress = kwargs.pop('progress', getattr(self, 'progress', None))
        self.warnings = kwargs.pop('warnings', False)
        kwargs.update({'dry_run': self.dry_run,
                       'progress': self.progress})
        self.setup()
        self.begin_transaction()
        changes = OrderedDict()

        try:
            for key in keys:
                importer = self.get_importer(key, **kwargs)
                if not importer:
                    log.warning("skipping unknown importer: {}".format(key))
                    continue

                created = importer.import_data()
                msg = "%s -> %s: added %s, updated 0, deleted 0 %s records"
                if self.dry_run:
                    msg += " (dry run)"
                logger = log.warning if created and self.warnings else log.info
                logger(msg, self.host_title, self.local_title, created, key)
                if created:
                    changes[key] = created
        except:
            if self.commit_host_partial and not self.dry_run:
                log.warning("{host} -> {local}: committing partial transaction on host {host} (despite error)".format(
                    host=self.host_title, local=self.local_title))
                self.commit_host_transaction()
            raise
        else:
            if self.dry_run:
                self.rollback_transaction()
            else:
                self.commit_transaction()

        self.teardown()
        return changes


class FromSQLAlchemyHandler(ImportHandler):
    """
    Handler for imports for which the host data source is represented by a
    SQLAlchemy engine and ORM.
    """
    host_session = None

    def make_host_session(self):
        """
        Subclasses must override this to define the host database connection.
        """
        raise NotImplementedError

    def get_importer_kwargs(self, key, **kwargs):
        kwargs = super(FromSQLAlchemyHandler, self).get_importer_kwargs(key, **kwargs)
        kwargs.setdefault('host_session', self.host_session)
        return kwargs

    def begin_host_transaction(self):
        self.host_session = self.make_host_session()

    def rollback_host_transaction(self):
        self.host_session.rollback()
        self.host_session.close()
        self.host_session = None

    def commit_host_transaction(self):
        self.host_session.commit()
        self.host_session.close()
        self.host_session = None


class ToSQLAlchemyHandler(ImportHandler):
    """
    Handler for imports which target a SQLAlchemy ORM on the local side.
    """
    session = None

    def make_session(self):
        """
        Subclasses must override this to define the local database connection.
        """
        raise NotImplementedError

    def get_importer_kwargs(self, key, **kwargs):
        kwargs = super(ToSQLAlchemyHandler, self).get_importer_kwargs(key, **kwargs)
        kwargs.setdefault('session', self.session)
        return kwargs

    def begin_local_transaction(self):
        self.session = self.make_session()

    def rollback_local_transaction(self):
        self.session.rollback()
        self.session.close()
        self.session = None

    def commit_local_transaction(self):
        self.session.commit()
        self.session.close()
        self.session = None


# TODO: this is still pretty hacky, but needed to get it in here for now
class RecordRenderer(object):
    """
    Record renderer for email notifications sent from data import jobs.
    """

    def __init__(self, config):
        self.config = config

    def __call__(self, record):
        return self.render(record)

    def render(self, record):
        """
        Render the given record.
        """
        key = record.__class__.__name__.lower()
        renderer = getattr(self, 'render_{}'.format(key), None)
        if renderer:
            return renderer(record)

        label = self.get_label(record)
        url = self.get_url(record)
        if url:
            return '<a href="{}">{}</a>'.format(url, label)
        return label

    def get_label(self, record):
        key = record.__class__.__name__.lower()
        label = getattr(self, 'label_{}'.format(key), self.label)
        return label(record)

    def label(self, record):
        return six.text_type(record)

    def get_url(self, record):
        """
        Fetch / generate a URL for the given data record.  You should *not*
        override this method, but do :meth:`url()` instead.
        """
        key = record.__class__.__name__.lower()
        url = getattr(self, 'url_{}'.format(key), self.url)
        return url(record)

    def url(self, record):
        """
        Fetch / generate a URL for the given data record.
        """
        if hasattr(record, 'uuid'):
            url = self.config.get('tailbone', 'url')
            if url:
                url = url.rstrip('/')
                name = '{}s'.format(record.__class__.__name__.lower())
                if name == 'persons': # FIXME, obviously this is a hack
                    name = 'people'
                url = '{}/{}/{{uuid}}'.format(url, name)
                return url.format(uuid=record.uuid)
