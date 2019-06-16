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
Views for generic product batches
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model
from rattail.util import OrderedDict

import colander

from tailbone import forms
from tailbone.views.batch import BatchMasterView


ACTION_OPTIONS = OrderedDict([
    ('make_label_batch', "Make a new Label Batch"),
    ('make_pricing_batch', "Make a new Pricing Batch"),
])


class ExecutionOptions(colander.Schema):

    action = colander.SchemaNode(
        colander.String(),
        validator=colander.OneOf(ACTION_OPTIONS),
        widget=forms.widgets.PlainSelectWidget(values=ACTION_OPTIONS.items()))


class ProductBatchView(BatchMasterView):
    """
    Master view for product batches.
    """
    model_class = model.ProductBatch
    model_row_class = model.ProductBatchRow
    default_handler_spec = 'rattail.batch.product:ProductBatchHandler'
    route_prefix = 'batch.product'
    url_prefix = '/batches/product'
    template_prefix = '/batch/product'
    downloadable = True
    cloneable = True
    execution_options_schema = ExecutionOptions
    rows_bulk_deletable = True

    form_fields = [
        'id',
        'input_filename',
        'description',
        'notes',
        'created',
        'created_by',
        'rowcount',
        'executed',
        'executed_by',
    ]

    row_labels = {
        'reportcode': "Report Code",
    }

    row_grid_columns = [
        'sequence',
        'upc',
        'brand_name',
        'description',
        'size',
        'department',
        'subdepartment',
        'vendor',
        'regular_cost',
        'current_cost',
        'regular_price',
        'current_price',
        'status_code',
    ]

    row_form_fields = [
        'sequence',
        'item_entry',
        'product',
        'item_id',
        'upc',
        'brand_name',
        'description',
        'size',
        'department_number',
        'department',
        'subdepartment_number',
        'subdepartment',
        'category',
        'family',
        'reportcode',
        'vendor',
        'vendor_item_code',
        'regular_cost',
        'current_cost',
        'current_cost_starts',
        'current_cost_ends',
        'regular_price',
        'current_price',
        'current_price_starts',
        'current_price_ends',
        'suggested_price',
        'status_code',
        'status_text',
    ]

    def configure_form(self, f):
        super(ProductBatchView, self).configure_form(f)

        # input_filename
        if self.creating:
            f.set_type('input_filename', 'file')
        else:
            f.set_readonly('input_filename')
            f.set_renderer('input_filename', self.render_downloadable_file)

    def configure_row_grid(self, g):
        super(ProductBatchView, self).configure_row_grid(g)

        g.set_joiner('vendor', lambda q: q.outerjoin(model.Vendor))
        g.set_sorter('vendor', model.Vendor.name)

        g.set_joiner('department', lambda q: q.outerjoin(model.Department))
        g.set_sorter('department', model.Department.name)

        g.set_joiner('subdepartment', lambda q: q.outerjoin(model.Subdepartment))
        g.set_sorter('subdepartment', model.Subdepartment.name)

        g.set_type('regular_cost', 'currency')
        g.set_type('current_cost', 'currency')
        g.set_type('regular_price', 'currency')
        g.set_type('current_price', 'currency')
        g.set_type('suggested_price', 'currency')

    def row_grid_extra_class(self, row, i):
        if row.status_code in (row.STATUS_MISSING_KEY,
                               row.STATUS_PRODUCT_NOT_FOUND):
            return 'warning'

    def configure_row_form(self, f):
        super(ProductBatchView, self).configure_row_form(f)

        f.set_type('upc', 'gpc')

        f.set_renderer('product', self.render_product)
        f.set_renderer('vendor', self.render_vendor)
        f.set_renderer('department', self.render_department)
        f.set_renderer('subdepartment', self.render_subdepartment)
        f.set_renderer('category', self.render_category)
        f.set_renderer('family', self.render_family)
        f.set_renderer('reportcode', self.render_report)

    def get_execute_success_url(self, batch, result, **kwargs):
        if kwargs['action'] == 'make_label_batch':
            return self.request.route_url('labels.batch.view', uuid=result.uuid)
        elif kwargs['action'] == 'make_pricing_batch':
            return self.request.route_url('batch.pricing.view', uuid=result.uuid)
        return super(ProductBatchView, self).get_execute_success_url(batch)

    def get_row_csv_fields(self):
        fields = super(ProductBatchView, self).get_row_csv_fields()

        if 'vendor_uuid' in fields:
            i = fields.index('vendor_uuid')
            fields.insert(i + 1, 'vendor_id')
            fields.insert(i + 2, 'vendor_abbreviation')
            fields.insert(i + 3, 'vendor_name')
        else:
            fields.append('vendor_id')
            fields.append('vendor_abbreviation')
            fields.append('vendor_name')

        if 'category_uuid' in fields:
            i = fields.index('category_uuid')
            fields.insert(i + 1, 'category_code')
            fields.insert(i + 2, 'category_name')
        else:
            fields.append('category_code')
            fields.append('category_name')

        if 'family_uuid' in fields:
            i = fields.index('family_uuid')
            fields.insert(i + 1, 'family_code')
            fields.insert(i + 2, 'family_name')
        else:
            fields.append('family_code')
            fields.append('family_name')

        if 'reportcode_uuid' in fields:
            i = fields.index('reportcode_uuid')
            fields.insert(i + 1, 'report_code')
            fields.insert(i + 2, 'report_name')
        else:
            fields.append('report_code')
            fields.append('report_name')

        return fields

    def supplement_row_data(self, row, fields, data):
        vendor = row.vendor
        if 'vendor_id' in fields:
            data['vendor_id'] = (vendor.id or '') if vendor else ''
        if 'vendor_abbreviation' in fields:
            data['vendor_abbreviation'] = (vendor.abbreviation or '') if vendor else ''
        if 'vendor_name' in fields:
            data['vendor_name'] = (vendor.name or '') if vendor else ''

        category = row.category
        if 'category_code' in fields:
            data['category_code'] = (category.code or '') if category else ''
        if 'category_name' in fields:
            data['category_name'] = (category.name or '') if category else ''

        family = row.family
        if 'family_code' in fields:
            data['family_code'] = (family.code or '') if family else ''
        if 'family_name' in fields:
            data['family_name'] = (family.name or '') if family else ''

        report = row.reportcode
        if 'report_code' in fields:
            data['report_code'] = (report.code or '') if report else ''
        if 'report_name' in fields:
            data['report_name'] = (report.name or '') if report else ''

    def get_row_csv_row(self, row, fields):
        csvrow = super(ProductBatchView, self).get_row_csv_row(row, fields)
        self.supplement_row_data(row, fields, csvrow)
        return csvrow

    def get_row_xlsx_row(self, row, fields):
        xlrow = super(ProductBatchView, self).get_row_xlsx_row(row, fields)
        self.supplement_row_data(row, fields, xlrow)
        return xlrow


def includeme(config):
    ProductBatchView.defaults(config)
