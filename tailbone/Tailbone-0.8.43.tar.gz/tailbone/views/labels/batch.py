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
Views for label batches
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail.db import model

from deform import widget as dfwidget
from webhelpers2.html import HTML, tags

from tailbone import forms
from tailbone.views.batch import BatchMasterView


class LabelBatchView(BatchMasterView):
    """
    Master view for label batches.
    """
    model_class = model.LabelBatch
    model_row_class = model.LabelBatchRow
    default_handler_spec = 'rattail.batch.labels:LabelBatchHandler'
    model_title_plural = "Label Batches"
    route_prefix = 'labels.batch'
    url_prefix = '/labels/batches'
    template_prefix = '/batch/labels'
    creatable = False
    rows_editable = True
    rows_bulk_deletable = True
    cloneable = True
    results_executable = True

    row_grid_columns = [
        'sequence',
        'upc',
        'brand_name',
        'description',
        'size',
        'regular_price',
        'sale_price',
        'label_profile',
        'label_quantity',
        'status_code',
    ]

    form_fields = [
        'id',
        'description',
        'static_prices',
        'label_profile',
        'notes',
        'created',
        'created_by',
        'handheld_batches',
        'rowcount',
        'executed',
        'executed_by',
    ]

    row_labels = {
        'upc': "UPC",
        'vendor_id': "Vendor ID",
        'label_profile': "Label Type",
    }

    row_form_fields = [
        'sequence',
        'upc',
        'product',
        'brand_name',
        'description',
        'size',
        'department_number',
        'department_name',
        'regular_price',
        'pack_quantity',
        'pack_price',
        'sale_price',
        'sale_start',
        'sale_stop',
        'vendor_id',
        'vendor_name',
        'vendor_item_code',
        'case_quantity',
        'label_profile',
        'label_quantity',
        'status_code',
        'status_text',
    ]

    def configure_form(self, f):
        super(LabelBatchView, self).configure_form(f)

        # handheld_batches
        f.set_readonly('handheld_batches')
        f.set_renderer('handheld_batches', self.render_handheld_batches)
        if self.viewing or self.deleting:
            batch = self.get_instance()
            if not batch._handhelds:
                f.remove_field('handheld_batches')

        # label profile
        if self.creating or self.editing:
            if 'label_profile' in f.fields:
                f.replace('label_profile', 'label_profile_uuid')
                # TODO: should restrict somehow? just allow override?
                profiles = self.Session.query(model.LabelProfile)
                values = [(p.uuid, six.text_type(p))
                          for p in profiles]
                require_profile = False
                if not require_profile:
                    values.insert(0, ('', "(none)"))
                f.set_widget('label_profile_uuid', dfwidget.SelectWidget(values=values))
                f.set_label('label_profile_uuid', "Label Profile")

    def render_handheld_batches(self, label_batch, field):
        items = ''
        for handheld in label_batch._handhelds:
            text = handheld.handheld.id_str
            url = self.request.route_url('batch.handheld.view', uuid=handheld.handheld_uuid)
            items += HTML.tag('li', c=tags.link_to(text, url))
        return HTML.tag('ul', c=items)

    def configure_row_grid(self, g):
        super(LabelBatchView, self).configure_row_grid(g)

        # short labels
        g.set_label('brand_name', "Brand")
        g.set_label('regular_price', "Reg Price")
        g.set_label('label_quantity', "Qty")

    def row_grid_extra_class(self, row, i):
        if row.status_code != row.STATUS_OK:
            return 'warning'

    def configure_row_form(self, f):
        super(LabelBatchView, self).configure_row_form(f)

        # readonly fields
        f.set_readonly('sequence')
        f.set_readonly('product')
        f.set_readonly('upc')
        f.set_readonly('brand_name')
        f.set_readonly('description')
        f.set_readonly('size')
        f.set_readonly('department_number')
        f.set_readonly('department_name')
        f.set_readonly('regular_price')
        f.set_readonly('pack_quantity')
        f.set_readonly('pack_price')
        f.set_readonly('sale_price')
        f.set_readonly('sale_start')
        f.set_readonly('sale_stop')
        f.set_readonly('vendor_id')
        f.set_readonly('vendor_name')
        f.set_readonly('vendor_item_code')
        f.set_readonly('case_quantity')
        f.set_readonly('status_code')
        f.set_readonly('status_text')

        if self.editing:
            f.remove_fields(
                'brand_name',
                'description',
                'size',
                'pack_quantity',
                'pack_price',
                'sale_start',
                'sale_stop',
                'vendor_id',
                'vendor_name',
                'vendor_item_code',
                'case_quantity',
            )
        else:
            f.remove_field('product')

        # label_profile
        if self.editing:
            f.replace('label_profile', 'label_profile_uuid')
            f.set_label('label_profile_uuid', "Label Type")
            profiles = self.Session.query(model.LabelProfile)\
                                   .filter(model.LabelProfile.visible == True)\
                                   .order_by(model.LabelProfile.ordinal)
            profile_values = [(p.uuid, six.text_type(p))
                              for p in profiles]
            f.set_widget('label_profile_uuid', forms.widgets.JQuerySelectWidget(values=profile_values))


def includeme(config):
    LabelBatchView.defaults(config)
