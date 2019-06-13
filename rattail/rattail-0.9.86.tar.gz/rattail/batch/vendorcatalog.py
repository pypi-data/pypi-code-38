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
Handler for Vendor Catalog batches
"""

from __future__ import unicode_literals, absolute_import

from sqlalchemy import orm

from rattail.db import model
from rattail.batch import BatchHandler
from rattail.vendors.catalogs import require_catalog_parser


class VendorCatalogHandler(BatchHandler):
    """
    Handler for vendor catalog batches.
    """
    batch_model_class = model.VendorCatalog

    version_catchup_execute = [
        'ProductCost',
    ]

    # TODO: change default for this, ultimately deprecate/remove
    use_legacy_update_status = True

    def should_populate(self, batch):
        # all vendor catalogs must come from data file
        return True

    def setup(self, batch, progress=None):
        self.vendor = batch.vendor
        self.products = {'upc': {}, 'vendor_code': {}}
        session = orm.object_session(batch)
        products = session.query(model.Product)\
                          .options(orm.joinedload(model.Product.brand))\
                          .options(orm.joinedload(model.Product.costs))

        def cache(product, i):
            if product.upc:
                self.products['upc'][product.upc] = product
            cost = product.cost_for_vendor(self.vendor)
            product.vendor_cost = cost
            if cost and cost.code:
                self.products['vendor_code'][cost.code] = product

        assert self.progress_loop(cache, products.all(), progress,
                                  message="Caching products by UPC and vendor code")

    setup_populate = setup
    setup_refresh = setup

    def populate(self, batch, progress=None):
        """
        Pre-fill batch with row data from an input data file, leveraging a
        specific catalog parser.
        """
        assert batch.filename and batch.parser_key
        session = orm.object_session(batch)
        path = batch.filepath(self.config)
        parser = require_catalog_parser(batch.parser_key)
        # TODO: should add `config` kwarg to CatalogParser constructor
        parser.config = self.config
        parser.session = session
        parser.vendor = batch.vendor
        batch.effective = parser.parse_effective_date(path)

        def append(row, i):
            self.add_row(batch, row)
            if i % 5000 == 0:
                session.flush()

        data = list(parser.parse_rows(path, progress=progress))
        self.progress_loop(append, data, progress,
                           message="Adding initial rows to batch")

    def identify_product(self, row):
        product = None
        if row.upc:
            product = self.products['upc'].get(row.upc)
        if not product and row.vendor_code:
            product = self.products['vendor_code'].get(row.vendor_code)
        return product

    def refresh_row(self, row):
        """
        Inspect a single row from a catalog, and set its attributes based on
        whether or not the product exists, if we already have a cost record for
        the vendor, if the catalog contains a change etc.  Note that the
        product lookup is done first by UPC and then by vendor item code.
        """
        row.product = self.identify_product(row)
        if not row.product:
            row.status_code = row.STATUS_PRODUCT_NOT_FOUND
            return

        row.upc = row.product.upc
        row.brand_name = row.product.brand.name if row.product.brand else None
        row.description = row.product.description
        row.size = row.product.size

        old_cost = row.product.vendor_cost
        if not old_cost:
            row.status_code = row.STATUS_NEW_COST
            return

        row.cost = old_cost
        row.old_vendor_code = old_cost.code
        row.old_case_size = old_cost.case_size

        # old_case_cost
        row.old_case_cost = old_cost.case_cost
        if row.case_cost is not None and row.old_case_cost is not None:
            row.case_cost_diff = row.case_cost - row.old_case_cost

        # old_unit_cost
        row.old_unit_cost = old_cost.unit_cost
        if row.unit_cost is not None and row.old_unit_cost is not None:
            row.unit_cost_diff = row.unit_cost - row.old_unit_cost

        # status
        # TODO: deprecate/remove legacy status
        if self.use_legacy_update_status:
            diff = self.cost_differs(row, old_cost)
            if diff:
                row.status_code = row.STATUS_UPDATE_COST
                row.status_text = diff
            else:
                row.status_code = row.STATUS_NO_CHANGE

        else:
            if row.vendor_code != row.old_vendor_code:
                row.status_code = row.STATUS_CHANGE_VENDOR_ITEM_CODE
                row.status_text = "new vendor item code {} differs from old code {}".format(
                    repr(row.vendor_code), repr(row.old_vendor_code))
            elif row.case_size != row.old_case_size:
                row.status_code = row.STATUS_CHANGE_CASE_SIZE
                row.status_text = "new case size {} differs from old case size {}".format(
                    repr(row.case_size), repr(row.old_case_size))
            elif row.case_cost != row.old_case_cost:
                row.status_code = row.STATUS_CHANGE_COST
                row.status_text = "new case cost {} differs from old cost {}".format(
                    repr(row.case_cost), repr(row.old_case_cost))
            elif row.unit_cost != row.old_unit_cost:
                row.status_code = row.STATUS_CHANGE_COST
                row.status_text = "new unit cost {} differs from old cost {}".format(
                    repr(row.unit_cost), repr(row.old_unit_cost))
            else:
                row.status_code = row.STATUS_NO_CHANGE

    def cost_differs(self, row, cost):
        """
        Compare a batch row with a cost record to determine whether they match
        or differ.
        """
        if row.vendor_code is not None and row.vendor_code != cost.code:
            return "new vendor code {} differs from old code {}".format(
                repr(row.vendor_code), repr(cost.code))
        if row.case_cost is not None and row.case_cost != cost.case_cost:
            return "new case cost {} differs from old cost {}".format(
                row.case_cost, cost.case_cost)
        if row.unit_cost is not None and row.unit_cost != cost.unit_cost:
            return "new unit cost {} differs from old cost {}".format(
                row.unit_cost, cost.unit_cost)
