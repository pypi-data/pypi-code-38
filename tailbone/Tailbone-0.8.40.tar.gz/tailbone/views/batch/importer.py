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
Views for importer batches
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy as sa

from rattail.db import model

import colander

from tailbone.views.batch import BatchMasterView


class ImporterBatchView(BatchMasterView):
    """
    Master view for importer batches.
    """
    model_class = model.ImporterBatch
    default_handler_spec = 'rattail.batch.importer:ImporterBatchHandler'
    model_title_plural = "Import / Export Batches"
    route_prefix = 'batch.importer'
    url_prefix = '/batches/importer'
    template_prefix = '/batch/importer'
    creatable = False
    refreshable = False
    bulk_deletable = True
    rows_downloadable_csv = False
    rows_bulk_deletable = True

    labels = {
        'host_title': "Source",
        'local_title': "Target",
        'importer_key': "Model",
    }

    grid_columns = [
        'id',
        'description',
        'host_title',
        'local_title',
        'importer_key',
        'created',
        'created_by',
        'rowcount',
        'executed',
        'executed_by',
    ]

    form_fields = [
        'id',
        'description',
        'import_handler_spec',
        'host_title',
        'local_title',
        'importer_key',
        'notes',
        'created',
        'created_by',
        'row_table',
        'rowcount',
        'executed',
        'executed_by',
    ]

    row_grid_columns = [
        'sequence',
        'object_key',
        'object_str',
        'status_code',
    ]

    def configure_form(self, f):
        super(ImporterBatchView, self).configure_form(f)

        # readonly fields
        f.set_readonly('import_handler_spec')
        f.set_readonly('host_title')
        f.set_readonly('local_title')
        f.set_readonly('importer_key')
        f.set_readonly('row_table')

    def make_status_breakdown(self, batch):
        # TODO: should implement this, just can't use batch.data_rows apparently
        pass

    def delete_instance(self, batch):
        self.make_row_table(batch.row_table)
        if self.current_row_table is not None:
            self.current_row_table.drop()
        super(ImporterBatchView, self).delete_instance(batch)

    def make_row_table(self, name):
        if not hasattr(self, 'current_row_table'):
            metadata = sa.MetaData(schema='batch', bind=self.Session.bind)
            try:
                self.current_row_table = sa.Table(name, metadata, autoload=True)
            except sa.exc.NoSuchTableError:
                self.current_row_table = None

    def get_row_data(self, batch):
        self.make_row_table(batch.row_table)
        return self.Session.query(self.current_row_table)

    def get_row_status_enum(self):
        return self.enum.IMPORTER_BATCH_ROW_STATUS

    def configure_row_grid(self, g):
        super(ImporterBatchView, self).configure_row_grid(g)

        def make_filter(field, **kwargs):
            column = getattr(self.current_row_table.c, field)
            g.set_filter(field, column, **kwargs)

        make_filter('object_key')
        make_filter('object_str')
        make_filter('status_code', label="Status",
                    value_enum=self.enum.IMPORTER_BATCH_ROW_STATUS)

        def make_sorter(field):
            column = getattr(self.current_row_table.c, field)
            g.sorters[field] = lambda q, d: q.order_by(getattr(column, d)())

        make_sorter('sequence')
        make_sorter('object_key')
        make_sorter('object_str')
        make_sorter('status_code')

        g.set_sort_defaults('sequence')

        g.set_label('object_str', "Object Description")

        g.set_link('sequence')
        g.set_link('object_key')
        g.set_link('object_str')

    def row_grid_extra_class(self, row, i):
        if row.status_code == self.enum.IMPORTER_BATCH_ROW_STATUS_DELETE:
            return 'warning'
        if row.status_code in (self.enum.IMPORTER_BATCH_ROW_STATUS_CREATE,
                               self.enum.IMPORTER_BATCH_ROW_STATUS_UPDATE):
            return 'notice'

    def get_row_action_route_kwargs(self, row):
        return {
            'uuid': self.current_row_table.name,
            'row_uuid': row.uuid,
        }

    def get_row_instance(self):
        batch_uuid = self.request.matchdict['uuid']
        row_uuid = self.request.matchdict['row_uuid']
        self.make_row_table(batch_uuid)
        return self.Session.query(self.current_row_table)\
                           .filter(self.current_row_table.c.uuid == row_uuid)\
                           .one()

    def get_parent(self, row):
        uuid = self.current_row_table.name
        return self.Session.query(model.ImporterBatch).get(uuid)

    def get_row_instance_title(self, row):
        if row.object_str:
            return row.object_str
        if row.object_key:
            return row.object_key
        return "Row {}".format(row.sequence)

    def template_kwargs_view_row(self, **kwargs):
        batch = kwargs['parent_instance']
        row = kwargs['instance']
        kwargs['batch'] = batch
        kwargs['instance_title'] = batch.id_str

        fields = set()
        old_values = {}
        new_values = {}
        for col in self.current_row_table.c:
            if col.name.startswith('key_'):
                field = col.name[4:]
                fields.add(field)
                old_values[field] = new_values[field] = getattr(row, col.name)
            elif col.name.startswith('pre_'):
                field = col.name[4:]
                fields.add(field)
                old_values[field] = getattr(row, col.name)
            elif col.name.startswith('post_'):
                field = col.name[5:]
                fields.add(field)
                new_values[field] = getattr(row, col.name)

        kwargs['diff_fields'] = sorted(fields)
        kwargs['diff_old_values'] = old_values
        kwargs['diff_new_values'] = new_values
        return kwargs

    def make_row_form(self, instance=None, **kwargs):
        fields = ['sequence', 'object_key', 'object_str', 'status_code']
        for col in self.current_row_table.c:
            if col.name.startswith('key_'):
                fields.append(col.name)

        if kwargs.get('fields') is None:
            kwargs['fields'] = fields

        row = dict([(field, getattr(instance, field))
                    for field in fields])
        row['status_text'] = instance.status_text

        kwargs.setdefault('schema', colander.Schema())
        kwargs.setdefault('cancel_url', None)
        return super(ImporterBatchView, self).make_row_form(instance=row, **kwargs)

    def configure_row_form(self, f):
        """
        Configure the row form.
        """
        # object_str
        f.set_label('object_str', "Object Description")

        # status_code
        f.set_renderer('status_code', self.render_row_status_code)
        f.set_label('status_code', "Status")

    def render_row_status_code(self, row, field):
        status = self.enum.IMPORTER_BATCH_ROW_STATUS[row['status_code']]
        if row['status_code'] == self.enum.IMPORTER_BATCH_ROW_STATUS_UPDATE and row['status_text']:
            return "{} ({})".format(status, row['status_text'])
        return status

    def delete_row(self):
        row = self.get_row_instance()
        if not row:
            raise self.notfound()

        batch = self.get_parent(row)
        query = self.current_row_table.delete().where(self.current_row_table.c.uuid == row.uuid)
        query.execute()
        batch.rowcount -= 1
        return self.redirect(self.get_action_url('view', batch))

    def bulk_delete_rows(self):
        batch = self.get_instance()
        query = self.get_effective_row_data(sort=False)
        batch.rowcount -= query.count()
        delete_query = self.current_row_table.delete().where(self.current_row_table.c.uuid.in_([row.uuid for row in query]))
        delete_query.execute()
        return self.redirect(self.get_action_url('view', batch))


def includeme(config):
    ImporterBatchView.defaults(config)
