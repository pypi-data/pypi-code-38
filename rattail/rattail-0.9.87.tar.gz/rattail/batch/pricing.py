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
Handler for pricing batches
"""

from __future__ import unicode_literals, absolute_import

import decimal

import six
from sqlalchemy import orm

from rattail.db import model, api
from rattail.gpc import GPC
from rattail.batch import BatchHandler
from rattail.excel import ExcelReader


class PricingBatchHandler(BatchHandler):
    """
    Handler for pricing batches.
    """
    batch_model_class = model.PricingBatch

    # cached decimal object used for rounding percentages, below
    percent_decimal = decimal.Decimal('.001')

    def should_populate(self, batch):
        if batch.input_filename:
            return True
        if hasattr(batch, 'products'):
            return True
        return False

    def populate(self, batch, progress=None):
        """
        Batch row data comes from product query.
        """
        if batch.input_filename:
            return self.populate_from_file(batch, progress=progress)

        if hasattr(batch, 'product_batch') and batch.product_batch:
            self.populate_from_product_batch(batch, progress=progress)
            return

        assert batch.products
        session = orm.object_session(batch)

        def append(item, i):
            row = model.PricingBatchRow()
            row.product = item
            row.upc = row.product.upc
            self.add_row(batch, row)
            if i % 200 == 0:
                session.flush()

        self.progress_loop(append, batch.products, progress,
                           message="Adding initial rows to batch")

    def populate_from_file(self, batch, progress=None):
        """
        Batch row data comes from input data file.
        """
        path = batch.filepath(self.config, filename=batch.input_filename)
        reader = ExcelReader(path)
        excel_rows = reader.read_rows(progress=progress)
        session = orm.object_session(batch)

        def append(excel, i):
            row = model.PricingBatchRow()

            row.item_entry = excel['upc']
            row.upc = GPC(row.item_entry, calc_check_digit='upc')
            row.product = api.get_product_by_upc(session, row.upc)

            self.add_row(batch, row)
            if i % 200 == 0:
                session.flush()

        self.progress_loop(append, excel_rows, progress,
                           message="Adding initial rows to batch")

    def populate_from_product_batch(self, batch, progress=None):
        """
        Populate pricing batch from product batch.
        """
        session = orm.object_session(batch)
        product_batch = batch.product_batch

        def add(prow, i):
            row = model.PricingBatchRow()
            row.item_entry = prow.item_entry
            with session.no_autoflush:
                row.product = prow.product
            self.add_row(batch, row)
            if i % 200 == 0:
                session.flush()

        self.progress_loop(add, product_batch.active_rows(), progress,
                           message="Adding initial rows to batch")

    def refresh_row(self, row):
        """
        Inspect a row from the source data and populate additional attributes
        for it, according to what we find in the database.
        """
        product = row.product
        if not product:
            row.status_code = row.STATUS_PRODUCT_NOT_FOUND
            return

        row.item_id = product.item_id
        row.upc = product.upc
        row.brand_name = six.text_type(product.brand or '')
        row.description = product.description
        row.size = product.size

        department = product.department
        row.department_number = department.number if department else None
        row.department_name = department.name if department else None

        subdept = product.subdepartment
        row.subdepartment_number = subdept.number if subdept else None
        row.subdepartment_name = subdept.name if subdept else None

        family = product.family
        row.family_code = family.code if family else None

        report = product.report_code
        row.report_code = report.code if report else None

        row.alternate_code = product.code

        cost = product.cost
        row.vendor = cost.vendor if cost else None
        row.vendor_item_code = cost.code if cost else None
        row.regular_unit_cost = cost.unit_cost if cost else None

        sugprice = product.suggested_price
        row.suggested_price = sugprice.price if sugprice else None

        regprice = product.regular_price
        row.old_price = regprice.price if regprice else None

    def set_status_per_diff(self, row):
        """
        Set the row's status code according to its price diff
        """
        # prefer "% Diff" if batch defines that
        threshold = row.batch.min_diff_percent
        if threshold:
            # force rounding of row's % diff, for comparison to threshold
            # (this is just to avoid unexpected surprises for the user)
            # (ideally we'd just flush() the session but this seems safer)
            if isinstance(row.price_diff_percent, decimal.Decimal):
                row.price_diff_percent = row.price_diff_percent.quantize(self.percent_decimal)
            # TODO: why don't we use price_diff_percent here again?
            minor = abs(row.margin_diff) < threshold

        else: # or, use "$ Diff" as fallback
            threshold = row.batch.min_diff_threshold
            minor = bool(threshold) and abs(row.price_diff) < threshold

        if row.price_diff > 0:
            if minor:
                row.status_code = row.STATUS_PRICE_INCREASE_MINOR
            else:
                row.status_code = row.STATUS_PRICE_INCREASE
        elif row.price_diff < 0:
            if minor:
                row.status_code = row.STATUS_PRICE_DECREASE_MINOR
            else:
                row.status_code = row.STATUS_PRICE_DECREASE
        else:
            row.status_code = row.STATUS_PRICE_UNCHANGED
