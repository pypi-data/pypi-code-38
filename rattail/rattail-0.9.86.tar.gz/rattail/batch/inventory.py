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
Handler for inventory batches
"""

from __future__ import unicode_literals, absolute_import

import six
from sqlalchemy import orm

from rattail.db import api, model
from rattail.batch import BatchHandler


class InventoryBatchHandler(BatchHandler):
    """
    Handler for inventory batches.
    """
    batch_model_class = model.InventoryBatch

    def init_batch(self, batch, **kwargs):
        if batch.total_cost is None:
            batch.total_cost = 0

    def should_populate(self, batch):
        if batch.handheld_batches:
            return True
        if batch.mode == self.enum.INVENTORY_MODE_ZERO_ALL:
            return True

    def populate(self, batch, progress=None):
        """
        Pre-fill batch with row data from an input data file, parsed according
        to the batch device type.
        """
        if batch.handheld_batches:
            self.populate_from_handheld(batch, progress=progress)
        elif batch.mode == self.enum.INVENTORY_MODE_ZERO_ALL:
            self.populate_zero_all(batch, progress=progress)

    def populate_from_handheld(self, batch, progress=None):

        def append(hh, i):
            row = model.InventoryBatchRow()
            row.upc = hh.upc
            row.cases = hh.cases or None
            row.units = hh.units or None
            self.add_row(batch, row)

        data = []
        for handheld in batch.handheld_batches:
            data.extend(handheld.active_rows())
        self.progress_loop(append, data, progress,
                           message="Adding initial rows to batch")

    def populate_zero_all(self, batch, progress=None):
        session = orm.object_session(batch)
        products = session.query(model.Product)\
                          .join(model.ProductInventory)\
                          .filter(model.ProductInventory.on_hand != None)\
                          .filter(model.ProductInventory.on_hand != 0)

        def append(product, i):
            row = model.InventoryBatchRow()
            row.product = product
            row.units = 0
            self.add_row(batch, row)

        self.progress_loop(append, products, progress,
                           message="Adding initial rows to batch")

    def refresh(self, batch, progress=None):
        batch.total_cost = 0

        # destroy and re-create data rows if batch is zero-all
        if batch.mode == self.enum.INVENTORY_MODE_ZERO_ALL:
            del batch.data_rows[:]
            batch.rowcount = 0
            self.populate_zero_all(batch, progress=progress)
            return True

        return super(InventoryBatchHandler, self).refresh(batch, progress=progress)

    def refresh_row(self, row):
        """
        Inspect a row from the source data and populate additional attributes
        for it, according to what we find in the database.
        """
        product = row.product
        if not product:
            if row.upc:
                session = orm.object_session(row)
                product = api.get_product_by_upc(session, row.upc)
            if not product:
                row.status_code = row.STATUS_PRODUCT_NOT_FOUND
                return

        # current / static attributes
        row.product = product
        row.upc = product.upc
        row.item_id = product.item_id
        row.brand_name = six.text_type(product.brand or '')
        row.description = product.description
        row.size = product.size
        row.status_code = row.STATUS_OK
        row.case_quantity = (product.cost.case_size or 1) if product.cost else 1

        if row.previous_units_on_hand is not None:
            row.variance = self.total_units(row) - row.previous_units_on_hand

        # TODO: is this a sufficient check?  need to avoid overwriting a cost
        # value which has been manually set, but this also means the first
        # value that lands will stick, and e.g. new cost would be ignored
        if row.unit_cost is None:
            row.unit_cost = self.get_unit_cost(row)

        self.refresh_totals(row)

    def total_units(self, row):
        return (row.cases or 0) * (row.case_quantity or 1) + (row.units or 0)

    def capture_current_units(self, row):
        """
        Capture the "current" (aka. "previous") unit count for the row, if
        applicable.
        """
        product = row.product
        if product and product.inventory:
            row.previous_units_on_hand = product.inventory.on_hand

    def refresh_totals(self, row):
        batch = row.batch

        if row.unit_cost is not None:
            row.total_cost = row.unit_cost * (row.full_unit_quantity or 0)
            batch.total_cost = (batch.total_cost or 0) + row.total_cost
        else:
            row.total_cost = None

    def get_unit_cost(self, row):
        if row.product and row.product.cost:
            return row.product.cost.unit_cost

    def execute(self, batch, progress=None, **kwargs):
        rows = batch.active_rows()
        self.update_rattail_inventory(batch, rows, progress=progress)
        return True

    def update_rattail_inventory(self, batch, rows, progress=None):

        def update(row, i):
            product = row.product
            inventory = product.inventory
            if not inventory:
                inventory = product.inventory = model.ProductInventory()
            inventory.on_hand = row.units

        self.progress_loop(update, rows, progress,
                           message="Updating local inventory")
