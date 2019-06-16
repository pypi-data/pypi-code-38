# -*- coding: utf-8 -*-
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
Handler for Vendor Invoice batches
"""

from __future__ import unicode_literals

import os

from sqlalchemy import orm

from rattail.db import api, model
from rattail.batch import BatchHandler
from rattail.vendors.invoices import require_invoice_parser


class VendorInvoiceHandler(BatchHandler):
    """
    Handler for vendor invoice batches.
    """
    batch_model_class = model.VendorInvoice
    po_number_title = "PO Number"

    def make_batch(self, session, progress=None, **kwargs):
        parser_key = kwargs.get('parser_key')
        if parser_key and not kwargs.get('vendor') and not kwargs.get('vendor_uuid'):
            parser = require_invoice_parser(parser_key)
            kwargs['vendor'] = api.get_vendor(session, parser.vendor_key)
        return super(VendorInvoiceHandler, self).make_batch(session, progress=progress, **kwargs)

    def should_populate(self, batch):
        # all vendor invoices must come from data file
        return True

    def setup_populate(self, batch, progress=None):
        self.vendor = batch.vendor

    def setup_refresh(self, batch, progress=None):
        self.vendor = batch.vendor

    def populate(self, batch, progress=None):
        """
        Pre-fill batch with row data from an input data file, leveraging a
        specific invoice parser.
        """
        assert batch.filename and batch.parser_key
        session = orm.object_session(batch)
        path = batch.filepath(self.config)
        parser = require_invoice_parser(batch.parser_key)
        parser.session = session
        parser.vendor = api.get_vendor(session, parser.vendor_key)
        assert batch.vendor is parser.vendor
        batch.invoice_date = parser.parse_invoice_date(path)
        self.setup_populate(batch, progress=progress)

        def append(row, i):
            self.add_row(batch, row)
            if i % 250 == 0:
                session.flush()

        data = list(parser.parse_rows(path))
        assert self.progress_loop(append, data, progress,
                                  message="Adding initial rows to batch")

        # if we have a PO number, attempt to reconcile against a purchase order
        if batch.purchase_order_number:
            purchase = self.get_purchase_order(batch.purchase_order_number)
            if purchase:
                self.cognize_purchase_order(session, batch, purchase, progress=progress)

    def get_purchase_order(self, number):
        """
        Fetch the purchase order object corresponding to the given PO number.
        Custom handlers should override this if aiming to reconcile invoices to
        purchase orders.
        """

    def validate_po_number(self, number):
        """
        This method does nothing by default.  Derived handlers can validate the
        PO number as they like.  Invalid PO numbers should cause ``ValueError``
        to be raised, with text of the reason for validation failure.
        """

    def find_product(self, row):
        """
        Attempt to locate the product for the row, based on UPC etc.
        """
        session = orm.object_session(row)

        if row.upc:
            product = self.find_product_by_upc(session, row.upc)
            if product:
                return product

        if row.vendor_code:
            product = self.find_product_by_vendor_code(session, row.vendor_code)
            if product:
                return product

    def find_product_by_upc(self, session, upc):
        if hasattr(self, 'products'):
            return self.products['upc'].get(upc)
        else:
            return api.get_product_by_upc(session, upc)

    def find_product_by_vendor_code(self, session, code):
        if hasattr(self, 'products'):
            return self.products['vendor_code'].get(code)
        else:
            return api.get_product_by_vendor_code(session, code, self.vendor)

    def refresh_row(self, row):
        """
        Inspect a single row from a invoice, and set its attributes based on
        whether or not the product exists, if we already have a cost record for
        the vendor, if the invoice contains a change etc.  Note that the
        product lookup is done first by UPC and then by vendor item code.
        """
        product = self.find_product(row)
        if not product:
            row.status_code = row.STATUS_NOT_IN_DB
            return

        row.product = product
        row.upc = product.upc
        row.brand_name = product.brand.name if product.brand else None
        row.description = product.description
        row.size = product.size

        # Calculate case cost if the parser couldn't provide one.
        if not row.case_cost and row.unit_cost and row.case_quantity:
            row.case_cost = row.unit_cost * row.case_quantity

        if not product.cost_for_vendor(self.vendor):
            row.status_code = row.STATUS_COST_NOT_IN_DB
        elif not row.case_quantity:
            row.status_code = row.STATUS_NO_CASE_QUANTITY
        else:
            row.status_code = row.STATUS_OK

    def cognize_purchase_order(self, session, invoice, purchase, progress=None):
        """
        Cognize the given invoice against the given purchase order object.
        Custom handlers should override this if aiming to reconcile invoices to
        purchase orders.
        """

    def execute(self, batch, **kwargs):
        """
        Execute the vendor invoice batch.  Note that the default handler does
        not perform any actions; a custom handler must be used for anything
        interesting to happen.
        """
        return True
