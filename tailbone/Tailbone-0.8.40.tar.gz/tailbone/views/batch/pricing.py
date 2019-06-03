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
Views for pricing batches
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

from webhelpers2.html import tags

from tailbone.views.batch import BatchMasterView


class PricingBatchView(BatchMasterView):
    """
    Master view for pricing batches.
    """
    model_class = model.PricingBatch
    model_row_class = model.PricingBatchRow
    default_handler_spec = 'rattail.batch.pricing:PricingBatchHandler'
    model_title_plural = "Pricing Batches"
    route_prefix = 'batch.pricing'
    url_prefix = '/batches/pricing'
    template_prefix = '/batch/pricing'
    creatable = True
    downloadable = True
    bulk_deletable = True
    rows_editable = True
    rows_bulk_deletable = True

    labels = {
        'min_diff_threshold': "Min $ Diff",
        'min_diff_percent': "Min % Diff",
    }

    grid_columns = [
        'id',
        'description',
        'created',
        'created_by',
        'rowcount',
        # 'status_code',
        # 'complete',
        'executed',
        'executed_by',
    ]

    form_fields = [
        'id',
        'input_filename',
        'description',
        'min_diff_threshold',
        'min_diff_percent',
        'calculate_for_manual',
        'notes',
        'created',
        'created_by',
        'rowcount',
        'executed',
        'executed_by',
    ]

    row_labels = {
        'upc': "UPC",
        'vendor_id': "Vendor ID",
        'regular_unit_cost': "Reg. Cost",
        'price_diff': "$ Diff",
        'price_diff_percent': "% Diff",
        'brand_name': "Brand",
        'price_markup': "Markup",
        'manually_priced': "Manual",
    }

    row_grid_columns = [
        'sequence',
        'upc',
        'brand_name',
        'description',
        'size',
        'vendor_id',
        'discounted_unit_cost',
        'old_price',
        'new_price',
        'price_margin',
        'price_diff',
        'price_diff_percent',
        'manually_priced',
        'status_code',
    ]

    row_form_fields = [
        'sequence',
        'product',
        'upc',
        'brand_name',
        'description',
        'size',
        'department_number',
        'department_name',
        'subdepartment_number',
        'subdepartment_name',
        'family_code',
        'report_code',
        'alternate_code',
        'vendor',
        'vendor_item_code',
        'regular_unit_cost',
        'discounted_unit_cost',
        'suggested_price',
        'old_price',
        'new_price',
        'price_diff',
        'price_diff_percent',
        'price_markup',
        'price_margin',
        'old_price_margin',
        'margin_diff',
        'status_code',
        'status_text',
    ]

    def configure_form(self, f):
        super(PricingBatchView, self).configure_form(f)

        f.set_type('min_diff_threshold', 'currency')

        # input_filename
        if self.creating:
            f.set_type('input_filename', 'file')
        else:
            f.set_readonly('input_filename')
            f.set_renderer('input_filename', self.render_downloadable_file)

    def get_batch_kwargs(self, batch, mobile=False):
        kwargs = super(PricingBatchView, self).get_batch_kwargs(batch, mobile=mobile)
        kwargs['min_diff_threshold'] = batch.min_diff_threshold
        kwargs['min_diff_percent'] = batch.min_diff_percent
        kwargs['calculate_for_manual'] = batch.calculate_for_manual
        return kwargs

    def configure_row_grid(self, g):
        super(PricingBatchView, self).configure_row_grid(g)

        g.set_joiner('vendor_id', lambda q: q.outerjoin(model.Vendor))
        g.set_sorter('vendor_id', model.Vendor.id)
        g.set_filter('vendor_id', model.Vendor.id)
        g.set_renderer('vendor_id', self.render_vendor_id)

        g.set_type('old_price', 'currency')
        g.set_type('new_price', 'currency')
        g.set_type('price_diff', 'currency')

    def render_vendor_id(self, row, field):
        vendor_id = row.vendor.id if row.vendor else None
        if not vendor_id:
            return ""
        return vendor_id

    def row_grid_extra_class(self, row, i):
        if row.status_code == row.STATUS_CANNOT_CALCULATE_PRICE:
            return 'warning'
        if row.status_code in (row.STATUS_PRICE_INCREASE, row.STATUS_PRICE_DECREASE):
            return 'notice'

    def configure_row_form(self, f):
        super(PricingBatchView, self).configure_row_form(f)

        # readonly fields
        f.set_readonly('product')
        f.set_readonly('upc')
        f.set_readonly('brand_name')
        f.set_readonly('description')
        f.set_readonly('size')
        f.set_readonly('department_number')
        f.set_readonly('department_name')
        f.set_readonly('vendor')

        # product
        f.set_renderer('product', self.render_product)

        # currency fields
        f.set_type('suggested_price', 'currency')
        f.set_type('old_price', 'currency')
        f.set_type('new_price', 'currency')
        f.set_type('price_diff', 'currency')

        # vendor
        f.set_renderer('vendor', self.render_vendor)

    def render_vendor(self, row, field):
        vendor = row.vendor
        if not vendor:
            return ""
        text = "({}) {}".format(vendor.id, vendor.name)
        url = self.request.route_url('vendors.view', uuid=vendor.uuid)
        return tags.link_to(text, url)

    def get_row_csv_fields(self):
        fields = super(PricingBatchView, self).get_row_csv_fields()

        if 'vendor_uuid' in fields:
            i = fields.index('vendor_uuid')
            fields.insert(i + 1, 'vendor_id')
            fields.insert(i + 2, 'vendor_abbreviation')
            fields.insert(i + 3, 'vendor_name')
        else:
            fields.append('vendor_id')
            fields.append('vendor_abbreviation')
            fields.append('vendor_name')

        return fields

    def get_row_csv_row(self, row, fields):
        csvrow = super(PricingBatchView, self).get_row_csv_row(row, fields)

        vendor = row.vendor
        if 'vendor_id' in fields:
            csvrow['vendor_id'] = (vendor.id or '') if vendor else ''
        if 'vendor_abbreviation' in fields:
            csvrow['vendor_abbreviation'] = (vendor.abbreviation or '') if vendor else ''
        if 'vendor_name' in fields:
            csvrow['vendor_name'] = (vendor.name or '') if vendor else ''

        return csvrow


def includeme(config):
    PricingBatchView.defaults(config)
