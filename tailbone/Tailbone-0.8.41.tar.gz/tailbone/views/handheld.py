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
Views for handheld batches
"""

from __future__ import unicode_literals, absolute_import

import os

from rattail.db import model
from rattail.util import OrderedDict

import colander
from webhelpers2.html import tags

from tailbone import forms
from tailbone.db import Session
from tailbone.views.batch import FileBatchMasterView


ACTION_OPTIONS = OrderedDict([
    ('make_label_batch', "Make a new Label Batch"),
    ('make_inventory_batch', "Make a new Inventory Batch"),
])


class ExecutionOptions(colander.Schema):

    action = colander.SchemaNode(
        colander.String(),
        validator=colander.OneOf(ACTION_OPTIONS),
        widget=forms.widgets.PlainSelectWidget(values=ACTION_OPTIONS.items()))


class HandheldBatchView(FileBatchMasterView):
    """
    Master view for handheld batches.
    """
    model_class = model.HandheldBatch
    default_handler_spec = 'rattail.batch.handheld:HandheldBatchHandler'
    model_title_plural = "Handheld Batches"
    route_prefix = 'batch.handheld'
    url_prefix = '/batch/handheld'
    execution_options_schema = ExecutionOptions
    editable = False
    results_executable = True

    model_row_class = model.HandheldBatchRow
    rows_creatable = False
    rows_editable = True

    grid_columns = [
        'id',
        'device_type',
        'device_name',
        'created',
        'created_by',
        'rowcount',
        'status_code',
        'executed',
    ]

    form_fields = [
        'id',
        'device_type',
        'device_name',
        'filename',
        'created',
        'created_by',
        'rowcount',
        'status_code',
        'executed',
        'executed_by',
    ]

    row_labels = {
        'upc': "UPC",
    }

    row_grid_columns = [
        'sequence',
        'upc',
        'brand_name',
        'description',
        'size',
        'cases',
        'units',
        'status_code',
    ]

    row_form_fields = [
        'sequence',
        'upc',
        'brand_name',
        'description',
        'size',
        'status_code',
        'cases',
        'units',
    ]

    def configure_grid(self, g):
        super(HandheldBatchView, self).configure_grid(g)
        device_types = OrderedDict(sorted(self.enum.HANDHELD_DEVICE_TYPE.items(),
                                          key=lambda item: item[1]))
        g.set_enum('device_type', device_types)

    def grid_extra_class(self, batch, i):
        if batch.status_code is not None and batch.status_code != batch.STATUS_OK:
            return 'notice'

    def configure_form(self, f):
        super(HandheldBatchView, self).configure_form(f)
        batch = f.model_instance

        # device_type
        device_types = OrderedDict(sorted(self.enum.HANDHELD_DEVICE_TYPE.items(),
                                          key=lambda item: item[1]))
        f.set_enum('device_type', device_types)
        f.widgets['device_type'].values.insert(0, ('', "(none)"))

        if self.creating:
            f.set_fields([
                'filename',
                'device_type',
                'device_name',
            ])

        if self.viewing:
            if batch.inventory_batch:
                f.append('inventory_batch')
                f.set_renderer('inventory_batch', self.render_inventory_batch)

    def render_inventory_batch(self, handheld_batch, field):
        batch = handheld_batch.inventory_batch
        if not batch:
            return ""
        text = batch.id_str
        url = self.request.route_url('batch.inventory.view', uuid=batch.uuid)
        return tags.link_to(text, url)

    def get_batch_kwargs(self, batch):
        kwargs = super(HandheldBatchView, self).get_batch_kwargs(batch)
        kwargs['device_type'] = batch.device_type
        kwargs['device_name'] = batch.device_name
        return kwargs

    def configure_row_grid(self, g):
        super(HandheldBatchView, self).configure_row_grid(g)
        g.set_type('cases', 'quantity')
        g.set_type('units', 'quantity')
        g.set_label('brand_name', "Brand")

    def row_grid_extra_class(self, row, i):
        if row.status_code == row.STATUS_PRODUCT_NOT_FOUND:
            return 'warning'

    def configure_row_form(self, f):
        super(HandheldBatchView, self).configure_row_form(f)

        # readonly fields
        f.set_readonly('upc')
        f.set_readonly('brand_name')
        f.set_readonly('description')
        f.set_readonly('size')

        # upc
        f.set_renderer('upc', self.render_upc)

    def render_upc(self, row, field):
        upc = row.upc
        if not upc:
            return ""
        text = upc.pretty()
        if row.product_uuid:
            url = self.request.route_url('products.view', uuid=row.product_uuid)
            return tags.link_to(text, url)
        return text

    def get_execute_success_url(self, batch, result, **kwargs):
        if kwargs['action'] == 'make_inventory_batch':
            return self.request.route_url('batch.inventory.view', uuid=result.uuid)
        elif kwargs['action'] == 'make_label_batch':
            return self.request.route_url('labels.batch.view', uuid=result.uuid)
        return super(HandheldBatchView, self).get_execute_success_url(batch)

    def get_execute_results_success_url(self, result, **kwargs):
        if result is True:
            # no batches were actually executed
            return self.get_index_url()
        batch = result
        return self.get_execute_success_url(batch, result, **kwargs)


def includeme(config):
    HandheldBatchView.defaults(config)
