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
Views for maintaining vendor invoices
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail.db import model, api
from rattail.vendors.invoices import iter_invoice_parsers, require_invoice_parser

# import formalchemy
import colander
from deform import widget as dfwidget

from tailbone.views.batch import FileBatchMasterView


class VendorInvoicesView(FileBatchMasterView):
    """
    Master view for vendor invoice batches.
    """
    model_class = model.VendorInvoice
    model_row_class = model.VendorInvoiceRow
    default_handler_spec = 'rattail.batch.vendorinvoice:VendorInvoiceHandler'
    url_prefix = '/vendors/invoices'

    grid_columns = [
        'id',
        'vendor',
        'invoice_date',
        'purchase_order_number',
        'filename',
        'created',
        'created_by',
        'executed',
    ]

    form_fields = [
        'id',
        'vendor',
        'filename',
        'parser_key',
        'purchase_order_number',
        'invoice_date',
        'created',
        'created_by',
        'executed',
        'executed_by',
    ]

    row_grid_columns = [
        'sequence',
        'upc',
        'brand_name',
        'description',
        'size',
        'vendor_code',
        'shipped_cases',
        'shipped_units',
        'unit_cost',
        'status_code',
    ]

    def get_instance_title(self, batch):
        return six.text_type(batch.vendor)

    def configure_grid(self, g):
        super(VendorInvoicesView, self).configure_grid(g)

        # vendor
        g.set_joiner('vendor', lambda q: q.join(model.Vendor))
        g.set_filter('vendor', model.Vendor.name,
                     default_active=True,
                     default_verb='contains')
        g.set_sorter('vendor', model.Vendor.name)
        g.set_link('vendor')

        # invoice_date
        g.set_link('invoice_date')

        # purchase_order_number
        g.set_link('purchase_order_number')

        # filename
        g.set_link('filename')

        # created
        g.set_link('created', False)

        # executed
        g.set_link('executed', False)

    def configure_form(self, f):
        super(VendorInvoicesView, self).configure_form(f)

        # vendor
        if self.creating:
            f.remove_field('vendor')
        else:
            f.set_readonly('vendor')

        # purchase_order_number
        f.set_label('purchase_order_number', self.handler.po_number_title)
        # f.set_validator('purchase_order_number', self.validate_po_number)

        # filename
        f.set_label('filename', "Invoice File")

        # invoice_date
        if self.creating:
            f.remove_field('invoice_date')
        else:
            f.set_readonly('invoice_date')

        # parser_key
        if self.creating:
            parsers = sorted(iter_invoice_parsers(), key=lambda p: p.display)
            parser_values = [(p.key, p.display) for p in parsers]
            parser_values.insert(0, ('', "(please choose)"))
            f.set_widget('parser_key', dfwidget.SelectWidget(values=parser_values))
            f.set_label('parser_key', "File Type")
        else:
            f.remove_field('parser_key')

    # TODO: this is not needed for now, and this whole thing should be merged
    # with the Purchasing Batch system anyway...
    # def validate_po_number(self, value, field):
    #     """
    #     Let the invoice handler in effect determine if the user-provided
    #     purchase order number is valid.
    #     """
    #     parser_key = field.parent.parser_key.value
    #     if not parser_key:
    #         raise formalchemy.ValidationError("Cannot validate PO number until File Type is chosen")
    #     parser = require_invoice_parser(parser_key)
    #     vendor = api.get_vendor(self.Session(), parser.vendor_key)
    #     try:
    #         self.handler.validate_po_number(value, vendor)
    #     except ValueError as error:
    #         raise formalchemy.ValidationError(unicode(error))

    def get_batch_kwargs(self, batch):
        kwargs = super(VendorInvoicesView, self).get_batch_kwargs(batch)
        kwargs['parser_key'] = batch.parser_key
        return kwargs

    def init_batch(self, batch):
        parser = require_invoice_parser(batch.parser_key)
        vendor = api.get_vendor(self.Session(), parser.vendor_key)
        if not vendor:
            self.request.session.flash("No vendor setting found in database for key: {}".format(parser.vendor_key))
            return False
        batch.vendor = vendor
        return True

    def configure_row_grid(self, g):
        super(VendorInvoicesView, self).configure_row_grid(g)
        g.set_label('upc', "UPC")
        g.set_label('brand_name', "Brand")
        g.set_label('shipped_cases', "Cases")
        g.set_label('shipped_units', "Units")

    def row_grid_extra_class(self, row, i):
        if row.status_code in (row.STATUS_NOT_IN_DB,
                               row.STATUS_COST_NOT_IN_DB,
                               row.STATUS_NO_CASE_QUANTITY):
            return 'warning'
        if row.status_code in (row.STATUS_NOT_IN_PURCHASE,
                               row.STATUS_NOT_IN_INVOICE,
                               row.STATUS_DIFFERS_FROM_PURCHASE):
            return 'notice'


def includeme(config):
    VendorInvoicesView.defaults(config)
