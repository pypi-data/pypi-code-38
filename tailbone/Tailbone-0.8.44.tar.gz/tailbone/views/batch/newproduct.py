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
Views for new product batches
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

from tailbone.views.batch import BatchMasterView


class NewProductBatchView(BatchMasterView):
    """
    Master view for new product batches.
    """
    model_class = model.NewProductBatch
    model_row_class = model.NewProductBatchRow
    default_handler_spec = 'rattail.batch.newproduct:NewProductBatchHandler'
    route_prefix = 'batch.newproduct'
    url_prefix = '/batches/newproduct'
    template_prefix = '/batch/newproduct'
    downloadable = True
    rows_editable = True

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
        'vendor_id': "Vendor ID",
    }

    row_grid_columns = [
        'sequence',
        'upc',
        'brand_name',
        'description',
        'size',
        'vendor',
        'vendor_item_code',
        'department',
        'subdepartment',
        'regular_price',
        'status_code',
    ]

    row_form_fields = [
        'sequence',
        'product',
        'upc',
        'brand_name',
        'description',
        'size',
        'vendor_id',
        'vendor',
        'vendor_item_code',
        'department_number',
        'department',
        'subdepartment_number',
        'subdepartment',
        'case_size',
        'case_cost',
        'unit_cost',
        'regular_price',
        'regular_price_multiple',
        'pack_price',
        'pack_price_multiple',
        'suggested_price',
        'category_code',
        'category',
        'family_code',
        'family',
        'report_code',
        'report',
        'status_code',
        'status_text',
    ]

    def configure_form(self, f):
        super(NewProductBatchView, self).configure_form(f)

        # input_filename
        if self.creating:
            f.set_type('input_filename', 'file')
        else:
            f.set_readonly('input_filename')
            f.set_renderer('input_filename', self.render_downloadable_file)

    def configure_row_grid(self, g):
        super(NewProductBatchView, self).configure_row_grid(g)

        g.set_type('case_cost', 'currency')
        g.set_type('unit_cost', 'currency')
        g.set_type('regular_price', 'currency')
        g.set_type('pack_price', 'currency')
        g.set_type('suggested_price', 'currency')

    def row_grid_extra_class(self, row, i):
        if row.status_code in (row.STATUS_MISSING_KEY,
                               row.STATUS_PRODUCT_EXISTS,
                               row.STATUS_VENDOR_NOT_FOUND,
                               row.STATUS_DEPT_NOT_FOUND,
                               row.STATUS_SUBDEPT_NOT_FOUND):
            return 'warning'
        if row.status_code in (row.STATUS_CATEGORY_NOT_FOUND,
                               row.STATUS_FAMILY_NOT_FOUND,
                               row.STATUS_REPORTCODE_NOT_FOUND):
            return 'notice'

    def configure_row_form(self, f):
        super(NewProductBatchView, self).configure_row_form(f)

        f.set_readonly('product')
        f.set_readonly('vendor')
        f.set_readonly('department')
        f.set_readonly('subdepartment')
        f.set_readonly('category')
        f.set_readonly('family')
        f.set_readonly('report')

        f.set_type('upc', 'gpc')

        f.set_renderer('vendor', self.render_vendor)
        f.set_renderer('department', self.render_department)
        f.set_renderer('subdepartment', self.render_subdepartment)
        f.set_renderer('report', self.render_report)


def includeme(config):
    NewProductBatchView.defaults(config)
