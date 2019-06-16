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
Handler for purchase order batches
"""

from __future__ import unicode_literals, absolute_import, division

import logging

import six
from sqlalchemy import orm

from rattail.db import model, api
from rattail.batch import BatchHandler
from rattail.time import localtime, make_utc
from rattail.vendors.invoices import require_invoice_parser


log = logging.getLogger(__name__)


class PurchaseBatchHandler(BatchHandler):
    """
    Handler for purchase order batches.
    """
    batch_model_class = model.PurchaseBatch

    def allow_cases(self):
        """
        Must return boolean indicating whether "cases" should be generally
        allowed, for sake of quantity input etc.
        """
        return self.config.getbool('rattail.batch', 'purchase.allow_cases',
                                   default=True)

    def allow_expired_credits(self):
        """
        Must return boolean indicating whether "expired" credits should be
        tracked.  In practice, this should either en- or dis-able various UI
        elements which involves expired product.
        """
        return self.config.getbool('rattail.batch', 'purchase.allow_expired_credits',
                                   default=True)

    def should_populate(self, batch):
        # TODO: this probably should change soon, for now this works..
        return batch.purchase and batch.mode in (self.enum.PURCHASE_BATCH_MODE_RECEIVING,
                                                 self.enum.PURCHASE_BATCH_MODE_COSTING)

    def populate(self, batch, progress=None):
        assert batch.purchase and batch.mode in (self.enum.PURCHASE_BATCH_MODE_RECEIVING,
                                                 self.enum.PURCHASE_BATCH_MODE_COSTING)
        batch.order_quantities_known = True

        # maybe copy receiving date from parent
        if batch.is_truck_dump_child() and not batch.date_received:
            batch.date_received = batch.truck_dump_batch.date_received

        def append(item, i):
            row = model.PurchaseBatchRow()
            product = item.product
            row.item = item
            row.product = product
            if product:
                row.upc = product.upc
                row.item_id = product.item_id
            else:
                row.upc = item.upc
                row.item_id = item.item_id
            row.cases_ordered = item.cases_ordered
            row.units_ordered = item.units_ordered
            row.cases_received = item.cases_received
            row.units_received = item.units_received
            row.po_unit_cost = item.po_unit_cost
            row.po_total = item.po_total
            if batch.mode == self.enum.PURCHASE_BATCH_MODE_COSTING:
                row.invoice_unit_cost = item.invoice_unit_cost
                row.invoice_total = item.invoice_total
            self.add_row(batch, row)

        self.progress_loop(append, batch.purchase.items, progress,
                           message="Adding initial rows to batch")

        # TODO: should(n't) this be handled elsewhere?
        session = orm.object_session(batch)
        session.flush()
        self.refresh_batch_status(batch)

    def populate_from_truck_dump_invoice(self, batch, progress=None):
        child_batch = batch
        parent_batch = child_batch.truck_dump_batch
        session = orm.object_session(child_batch)

        parser = require_invoice_parser(child_batch.invoice_parser_key)
        parser.session = session

        parser.vendor = api.get_vendor(session, parser.vendor_key)
        if parser.vendor is not child_batch.vendor:
            raise RuntimeError("Parser is for vendor '{}' but batch is for: {}".format(
                parser.vendor_key, child_batch.vendor))

        path = child_batch.filepath(self.config, child_batch.invoice_file)
        child_batch.invoice_date = parser.parse_invoice_date(path)
        child_batch.order_quantities_known = True

        def append(invoice_row, i):
            row = self.make_row_from_invoice(child_batch, invoice_row)
            self.add_row(child_batch, row)

        self.progress_loop(append, list(parser.parse_rows(path)), progress,
                           message="Adding initial rows to batch")

        if parent_batch.truck_dump_children_first:
            # children first, so should add rows to parent batch now
            session.flush()

            def append(child_row, i):
                if not child_row.out_of_stock:

                    # if row for this product already exists in parent, must aggregate
                    parent_row = self.locate_parent_row_for_child(parent_batch, child_row)
                    if parent_row:

                        # confirm 'case_quantity' matches
                        if parent_row.case_quantity != child_row.case_quantity:
                            raise ValueError("differing 'case_quantity' for item {}: {}".format(
                                child_row.item_entry, child_row.description))

                        # confirm 'out_of_stock' matches
                        if parent_row.out_of_stock != child_row.out_of_stock:
                            raise ValueError("differing 'out_of_stock' for item {}: {}".format(
                                cihld_row.item_entry, child_row.description))

                        # confirm 'invoice_unit_cost' matches
                        if parent_row.invoice_unit_cost != child_row.invoice_unit_cost:
                            raise ValueError("differing 'invoice_unit_cost' for item {}: {}".format(
                                cihld_row.item_entry, child_row.description))

                        # confirm 'invoice_case_cost' matches
                        if parent_row.invoice_case_cost != child_row.invoice_case_cost:
                            raise ValueError("differing 'invoice_case_cost' for item {}: {}".format(
                                cihld_row.item_entry, child_row.description))

                        # add 'ordered' quantities
                        if child_row.cases_ordered:
                            parent_row.cases_ordered = (parent_row.cases_ordered or 0) + child_row.cases_ordered
                        if child_row.units_ordered:
                            parent_row.units_ordered = (parent_row.units_ordered or 0) + child_row.units_ordered

                        # add 'shipped' quantities
                        if child_row.cases_shipped:
                            parent_row.cases_shipped = (parent_row.cases_shipped or 0) + child_row.cases_shipped
                        if child_row.units_shipped:
                            parent_row.units_shipped = (parent_row.units_shipped or 0) + child_row.units_shipped

                        # add 'invoice_total' quantities
                        if child_row.invoice_total:
                            parent_row.invoice_total = (parent_row.invoice_total or 0) + child_row.invoice_total
                            parent_batch.invoice_total = (parent_batch.invoice_total or 0) + child_row.invoice_total
                        if child_row.invoice_total_calculated:
                            parent_row.invoice_total_calculated = (parent_row.invoice_total_calculated or 0) + child_row.invoice_total_calculated
                            parent_batch.invoice_total_calculated = (parent_batch.invoice_total_calculated or 0) + child_row.invoice_total_calculated

                    else: # new product; simply add new row to parent
                        parent_row = self.make_parent_row_from_child(child_row)
                        self.add_row(parent_batch, parent_row)

            self.progress_loop(append, child_batch.active_rows(), progress,
                               message="Adding rows to parent batch")

        else: # children last, so should make parent claims now
            self.make_truck_dump_claims_for_child_batch(child_batch, progress=progress)

        self.refresh_batch_status(parent_batch)

    def locate_parent_row_for_child(self, parent_batch, child_row):
        """
        Locate a row within parent batch, which "matches" given row from child
        batch.  May return ``None`` if no match found.
        """
        if child_row.product_uuid:
            rows = [row for row in parent_batch.active_rows()
                    if row.product_uuid == child_row.product_uuid]
            if rows:
                return rows[0]

        elif child_row.item_entry:
            rows = [row for row in parent_batch.active_rows()
                    if row.product_uuid is None
                    and row.item_entry == child_row.item_entry]
            if rows:
                return rows[0]

    def make_row_from_invoice(self, batch, invoice_row):
        row = model.PurchaseBatchRow()
        row.item_entry = invoice_row.item_entry
        row.upc = invoice_row.upc
        row.vendor_code = invoice_row.vendor_code
        row.brand_name = invoice_row.brand_name
        row.description = invoice_row.description
        row.size = invoice_row.size
        row.case_quantity = invoice_row.case_quantity
        row.cases_ordered = invoice_row.ordered_cases
        row.units_ordered = invoice_row.ordered_units
        row.cases_shipped = invoice_row.shipped_cases
        row.units_shipped = invoice_row.shipped_units
        row.out_of_stock = invoice_row.out_of_stock
        row.invoice_unit_cost = invoice_row.unit_cost
        row.invoice_total = invoice_row.total_cost
        row.invoice_case_cost = invoice_row.case_cost
        return row

    def make_parent_row_from_child(self, child_row):
        row = model.PurchaseBatchRow()
        row.item_entry = child_row.item_entry
        row.upc = child_row.upc
        row.vendor_code = child_row.vendor_code
        row.brand_name = child_row.brand_name
        row.description = child_row.description
        row.size = child_row.size
        row.case_quantity = child_row.case_quantity
        row.cases_ordered = child_row.cases_ordered
        row.units_ordered = child_row.units_ordered
        row.cases_shipped = child_row.cases_shipped
        row.units_shipped = child_row.units_shipped
        row.out_of_stock = child_row.out_of_stock
        row.invoice_unit_cost = child_row.invoice_unit_cost
        row.invoice_total = child_row.invoice_total
        row.invoice_case_cost = child_row.invoice_case_cost
        return row

    def make_truck_dump_claims_for_child_batch(self, batch, progress=None):
        """
        Make all "claims" against a truck dump, for the given child batch.
        This assumes no claims exist for the child batch at time of calling,
        and that the truck dump batch is complete and not yet executed.
        """
        session = orm.object_session(batch)
        truck_dump_rows = batch.truck_dump_batch.active_rows()
        child_rows = batch.active_rows()

        # organize truck dump by product and UPC
        truck_dump_by_product = {}
        truck_dump_by_upc = {}

        def organize_parent(row, i):
            if row.product:
                truck_dump_by_product.setdefault(row.product.uuid, []).append(row)
            if row.upc:
                truck_dump_by_upc.setdefault(row.upc, []).append(row)

        self.progress_loop(organize_parent, truck_dump_rows, progress,
                           message="Organizing truck dump parent rows")

        # organize child batch by product and UPC
        child_by_product = {}
        child_by_upc = {}

        def organize_child(row, i):
            if row.product:
                child_by_product.setdefault(row.product.uuid, []).append(row)
            if row.upc:
                child_by_upc.setdefault(row.upc, []).append(row)

        self.progress_loop(organize_child, child_rows, progress,
                           message="Organizing truck dump child rows")

        # okay then, let's go through all our organized rows, and make claims

        def make_claims(child_product, i):
            uuid, child_product_rows = child_product
            if uuid in truck_dump_by_product:
                truck_dump_product_rows = truck_dump_by_product[uuid]
                for truck_dump_row in truck_dump_product_rows:
                    self.make_truck_dump_claims(truck_dump_row, child_product_rows)

        self.progress_loop(make_claims, child_by_product.items(), progress,
                           count=len(child_by_product),
                           message="Claiming parent rows for child") # (pass #1)

    def make_truck_dump_claims(self, truck_dump_row, child_rows):

        # first we go through the truck dump parent row, and calculate all
        # "present", and "claimed" vs. "pending" product quantities

        # cases_received
        cases_received = truck_dump_row.cases_received or 0
        cases_received_claimed = sum([claim.cases_received or 0
                                      for claim in truck_dump_row.claims])
        cases_received_pending = cases_received - cases_received_claimed

        # units_received
        units_received = truck_dump_row.units_received or 0
        units_received_claimed = sum([claim.units_received or 0
                                      for claim in truck_dump_row.claims])
        units_received_pending = units_received - units_received_claimed

        # cases_damaged
        cases_damaged = truck_dump_row.cases_damaged or 0
        cases_damaged_claimed = sum([claim.cases_damaged or 0
                                     for claim in truck_dump_row.claims])
        cases_damaged_pending = cases_damaged - cases_damaged_claimed

        # units_damaged
        units_damaged = truck_dump_row.units_damaged or 0
        units_damaged_claimed = sum([claim.units_damaged or 0
                                     for claim in truck_dump_row.claims])
        units_damaged_pending = units_damaged - units_damaged_claimed

        # cases_expired
        cases_expired = truck_dump_row.cases_expired or 0
        cases_expired_claimed = sum([claim.cases_expired or 0
                                     for claim in truck_dump_row.claims])
        cases_expired_pending = cases_expired - cases_expired_claimed

        # units_expired
        units_expired = truck_dump_row.units_expired or 0
        units_expired_claimed = sum([claim.units_expired or 0
                                     for claim in truck_dump_row.claims])
        units_expired_pending = units_expired - units_expired_claimed

        # TODO: should be calculating mispicks here too, right?

        def make_claim(child_row):
            c = model.PurchaseBatchRowClaim()
            c.claiming_row = child_row
            truck_dump_row.claims.append(c)
            return c

        for child_row in child_rows:

            # stop now if everything in this parent row is accounted for
            if not (cases_received_pending or units_received_pending
                    or cases_damaged_pending or units_damaged_pending
                    or cases_expired_pending or units_expired_pending):
                break

            # for each child row we also calculate all "present", and "claimed"
            # vs. "pending" product quantities

            # cases_shipped
            cases_shipped = child_row.cases_shipped or 0
            cases_shipped_claimed = sum([(claim.cases_received or 0)
                                         + (claim.cases_damaged or 0)
                                         + (claim.cases_expired or 0)
                                         for claim in child_row.truck_dump_claims])
            cases_shipped_pending = cases_shipped - cases_shipped_claimed

            # units_shipped
            units_shipped = child_row.units_shipped or 0
            units_shipped_claimed = sum([(claim.units_received or 0)
                                         + (claim.units_damaged or 0)
                                         + (claim.units_expired or 0)
                                         for claim in child_row.truck_dump_claims])
            units_shipped_pending = units_shipped - units_shipped_claimed

            # skip this child row if everything in it is accounted for
            if not (cases_shipped_pending or units_shipped_pending):
                continue

            # there should only be one claim for this parent/child combo
            claim = None

            # let's cache this
            case_quantity = child_row.case_quantity

            # make case claims
            if cases_shipped_pending and cases_received_pending:
                claim = claim or make_claim(child_row)
                if cases_received_pending >= cases_shipped_pending:
                    claim.cases_received = (claim.cases_received or 0) + cases_shipped_pending
                    child_row.cases_received = (child_row.cases_received or 0) + cases_shipped_pending
                    cases_received_pending -= cases_shipped_pending
                    cases_shipped_pending = 0
                else: # shipped > received
                    claim.cases_received = (claim.cases_received or 0) + cases_received_pending
                    child_row.cases_received = (child_row.cases_received or 0) + cases_received_pending
                    cases_shipped_pending -= cases_received_pending
                    cases_received_pending = 0
                self.refresh_row(child_row)
            if cases_shipped_pending and cases_damaged_pending:
                claim = claim or make_claim(child_row)
                if cases_damaged_pending >= cases_shipped_pending:
                    claim.cases_damaged = (claim.cases_damaged or 0) + cases_shipped_pending
                    child_row.cases_damaged = (child_row.cases_damaged or 0) + cases_shipped_pending
                    cases_damaged_pending -= cases_shipped_pending
                    cases_shipped_pending = 0
                else: # shipped > damaged
                    claim.cases_damaged = (claim.cases_damaged or 0) + cases_damaged_pending
                    child_row.cases_damaged = (child_row.cases_damaged or 0) + cases_damaged_pending
                    cases_shipped_pending -= cases_damaged_pending
                    cases_damaged_pending = 0
                self.refresh_row(child_row)
            if cases_shipped_pending and cases_expired_pending:
                claim = claim or make_claim(child_row)
                if cases_expired_pending >= cases_shipped_pending:
                    claim.cases_expired = (claim.cases_expired or 0) + cases_shipped_pending
                    child_row.cases_expired = (child_row.cases_expired or 0) + cases_shipped_pending
                    cases_expired_pending -= cases_shipped_pending
                    cases_shipped_pending = 0
                else: # shipped > expired
                    claim.cases_expired = (claim.cases_expired or 0) + cases_expired_pending
                    child_row.cases_expired = (child_row.cases_expired or 0) + cases_expired_pending
                    cases_shipped_pending -= cases_expired_pending
                    cases_expired_pending = 0
                self.refresh_row(child_row)

            # make unit claims
            if units_shipped_pending and units_received_pending:
                claim = claim or make_claim(child_row)
                if units_received_pending >= units_shipped_pending:
                    claim.units_received = (claim.units_received or 0) + units_shipped_pending
                    child_row.units_received = (child_row.units_received or 0) + units_shipped_pending
                    units_received_pending -= units_shipped_pending
                    units_shipped_pending = 0
                else: # shipped > received
                    claim.units_received = (claim.units_received or 0) + units_received_pending
                    child_row.units_received = (child_row.units_received or 0) + units_received_pending
                    units_shipped_pending -= units_received_pending
                    units_received_pending = 0
                self.refresh_row(child_row)
            if units_shipped_pending and units_damaged_pending:
                claim = claim or make_claim(child_row)
                if units_damaged_pending >= units_shipped_pending:
                    claim.units_damaged = (claim.units_damaged or 0) + units_shipped_pending
                    child_row.units_damaged = (child_row.units_damaged or 0) + units_shipped_pending
                    units_damaged_pending -= units_shipped_pending
                    units_shipped_pending = 0
                else: # shipped > damaged
                    claim.units_damaged = (claim.units_damaged or 0) + units_damaged_pending
                    child_row.units_damaged = (child_row.units_damaged or 0) + units_damaged_pending
                    units_shipped_pending -= units_damaged_pending
                    units_damaged_pending = 0
                self.refresh_row(child_row)
            if units_shipped_pending and units_expired_pending:
                claim = claim or make_claim(child_row)
                if units_expired_pending >= units_shipped_pending:
                    claim.units_expired = (claim.units_expired or 0) + units_shipped_pending
                    child_row.units_expired = (child_row.units_expired or 0) + units_shipped_pending
                    units_expired_pending -= units_shipped_pending
                    units_shipped_pending = 0
                else: # shipped > expired
                    claim.units_expired = (claim.units_expired or 0) + units_expired_pending
                    child_row.units_expired = (child_row.units_expired or 0) + units_expired_pending
                    units_shipped_pending -= units_expired_pending
                    units_expired_pending = 0
                self.refresh_row(child_row)

            # claim units from parent, as cases for child.  note that this
            # crosses the case/unit boundary, but is considered "safe" because
            # we assume the child row has correct case quantity even if parent
            # row has a different one.
            if cases_shipped_pending and units_received_pending:
                received = units_received_pending // case_quantity
                if received:
                    claim = claim or make_claim(child_row)
                    if received >= cases_shipped_pending:
                        claim.cases_received = (claim.cases_received or 0) + cases_shipped_pending
                        child_row.cases_received = (child_row.units_received or 0) + cases_shipped_pending
                        units_received_pending -= (cases_shipped_pending * case_quantity)
                        cases_shipped_pending = 0
                    else: # shipped > received
                        claim.cases_received = (claim.cases_received or 0) + received
                        child_row.cases_received = (child_row.units_received or 0) + received
                        cases_shipped_pending -= received
                        units_received_pending -= (received * case_quantity)
                    self.refresh_row(child_row)
            if cases_shipped_pending and units_damaged_pending:
                damaged = units_damaged_pending // case_quantity
                if damaged:
                    claim = claim or make_claim(child_row)
                    if damaged >= cases_shipped_pending:
                        claim.cases_damaged = (claim.cases_damaged or 0) + cases_shipped_pending
                        child_row.cases_damaged = (child_row.units_damaged or 0) + cases_shipped_pending
                        units_damaged_pending -= (cases_shipped_pending * case_quantity)
                        cases_shipped_pending = 0
                    else: # shipped > damaged
                        claim.cases_damaged = (claim.cases_damaged or 0) + damaged
                        child_row.cases_damaged = (child_row.units_damaged or 0) + damaged
                        cases_shipped_pending -= damaged
                        units_damaged_pending -= (damaged * case_quantity)
                    self.refresh_row(child_row)
            if cases_shipped_pending and units_expired_pending:
                expired = units_expired_pending // case_quantity
                if expired:
                    claim = claim or make_claim(child_row)
                    if expired >= cases_shipped_pending:
                        claim.cases_expired = (claim.cases_expired or 0) + cases_shipped_pending
                        child_row.cases_expired = (child_row.units_expired or 0) + cases_shipped_pending
                        units_expired_pending -= (cases_shipped_pending * case_quantity)
                        cases_shipped_pending = 0
                    else: # shipped > expired
                        claim.cases_expired = (claim.cases_expired or 0) + expired
                        child_row.cases_expired = (child_row.units_expired or 0) + expired
                        cases_shipped_pending -= expired
                        units_expired_pending -= (expired * case_quantity)
                    self.refresh_row(child_row)

            # if necessary, try to claim cases from parent, as units for child.
            # this also crosses the case/unit boundary but is considered safe
            # only if the case quantity matches between child and parent rows.
            # (otherwise who knows what could go wrong.)
            if case_quantity == truck_dump_row.case_quantity:
                if units_shipped_pending and cases_received_pending:
                    received = cases_received_pending * case_quantity
                    claim = claim or make_claim(child_row)
                    if received >= units_shipped_pending:
                        claim.units_received = (claim.units_received or 0) + units_shipped_pending
                        child_row.units_received = (child_row.units_received or 0) + units_shipped_pending
                        leftover = received % units_shipped_pending
                        if leftover == 0:
                            cases_received_pending -= (received // units_shipped_pending)
                        else:
                            cases_received_pending -= (received // units_shipped_pending) - 1
                            units_received_pending += leftover
                        units_shipped_pending = 0
                    else: # shipped > received
                        claim.units_received = (claim.units_received or 0) + received
                        child_row.units_received = (child_row.units_received or 0) + received
                        units_shipped_pending -= received
                        cases_received_pending = 0
                    self.refresh_row(child_row)
                if units_shipped_pending and cases_damaged_pending:
                    damaged = cases_damaged_pending * case_quantity
                    claim = claim or make_claim(child_row)
                    if damaged >= units_shipped_pending:
                        claim.units_damaged = (claim.units_damaged or 0) + units_shipped_pending
                        child_row.units_damaged = (child_row.units_damaged or 0) + units_shipped_pending
                        leftover = damaged % units_shipped_pending
                        if leftover == 0:
                            cases_damaged_pending -= (damaged // units_shipped_pending)
                        else:
                            cases_damaged_pending -= (damaged // units_shipped_pending) - 1
                            units_damaged_pending += leftover
                        units_shipped_pending = 0
                    else: # shipped > damaged
                        claim.units_damaged = (claim.units_damaged or 0) + damaged
                        child_row.units_damaged = (child_row.units_damaged or 0) + damaged
                        units_shipped_pending -= damaged
                        cases_damaged_pending = 0
                    self.refresh_row(child_row)
                if units_shipped_pending and cases_expired_pending:
                    expired = cases_expired_pending * case_quantity
                    claim = claim or make_claim(child_row)
                    if expired >= units_shipped_pending:
                        claim.units_expired = (claim.units_expired or 0) + units_shipped_pending
                        child_row.units_expired = (child_row.units_expired or 0) + units_shipped_pending
                        leftover = expired % units_shipped_pending
                        if leftover == 0:
                            cases_expired_pending -= (expired // units_shipped_pending)
                        else:
                            cases_expired_pending -= (expired // units_shipped_pending) - 1
                            units_expired_pending += leftover
                        units_shipped_pending = 0
                    else: # shipped > expired
                        claim.units_expired = (claim.units_expired or 0) + expired
                        child_row.units_expired = (child_row.units_expired or 0) + expired
                        units_shipped_pending -= expired
                        cases_expired_pending = 0
                    self.refresh_row(child_row)

            # refresh the parent row, to reflect any new claim(s) made
            self.refresh_row(truck_dump_row)

    # TODO: surely this should live elsewhere
    def calc_best_fit(self, units, case_quantity):
        case_quantity = case_quantity or 1
        if case_quantity == 1:
            return 0, units
        cases = units // case_quantity
        if cases:
            return cases, units - (cases * case_quantity)
        return 0, units

    def refresh(self, batch, progress=None):

        # refresh all rows etc. per usual
        result = super(PurchaseBatchHandler, self).refresh(batch, progress=progress)
        if result:

            # here begins some extra magic for truck dump receiving batches
            if batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
                session = orm.object_session(batch)
                session.flush()

                if batch.is_truck_dump_parent():

                    # will try to establish new claims against the parent
                    # batch, where possible
                    unclaimed = [row for row in batch.active_rows()
                                 if row.status_code in (row.STATUS_TRUCKDUMP_UNCLAIMED,
                                                        row.STATUS_TRUCKDUMP_PARTCLAIMED)]
                    for row in unclaimed:
                        if row.product_uuid: # only support rows with product for now
                            self.make_truck_dump_claims_for_parent_row(row)

                    # all rows should be refreshed now, but batch status still needs it
                    self.refresh_batch_status(batch)
                    for child in batch.truck_dump_children:
                        self.refresh_batch_status(child)

                elif batch.is_truck_dump_child():

                    # will try to establish claims against the parent batch,
                    # for each "incomplete" row (i.e. those with unclaimed
                    # order quantities)
                    incomplete = [row for row in batch.active_rows()
                                  if row.status_code in (row.STATUS_INCOMPLETE,
                                                         row.STATUS_ORDERED_RECEIVED_DIFFER)]
                    for row in incomplete:
                        if row.product_uuid: # only support rows with product for now
                            parent_rows = [parent_row for parent_row in batch.truck_dump_batch.active_rows()
                                           if parent_row.product_uuid == row.product_uuid]
                            for parent_row in parent_rows:
                                self.make_truck_dump_claims(parent_row, [row])
                                if row.status_code not in (row.STATUS_INCOMPLETE,
                                                           row.STATUS_ORDERED_RECEIVED_DIFFER):
                                    break

                    # all rows should be refreshed now, but batch status still needs it
                    self.refresh_batch_status(batch.truck_dump_batch)
                    self.refresh_batch_status(batch)

        return result

    def refresh_batch_status(self, batch):
        rows = batch.active_rows()

        # "unknown product" is the most egregious status; we'll "prefer" it
        # over all others in order to bring it to user's attention
        if any([row.status_code == row.STATUS_PRODUCT_NOT_FOUND for row in rows]):
            batch.status_code = batch.STATUS_UNKNOWN_PRODUCT

        # for now anything else is considered ok
        else:
            batch.status_code = batch.STATUS_OK

        # truck dump parent batch gets status to reflect how much is (un)claimed
        if batch.is_truck_dump_parent():

            # batch is "claimed" only if all rows are "settled" so to speak
            if all([row.truck_dump_status == row.STATUS_TRUCKDUMP_CLAIMED
                    for row in rows]):
                batch.truck_dump_status = batch.STATUS_TRUCKDUMP_CLAIMED

            # otherwise just call it "unclaimed"
            else:
                batch.truck_dump_status = batch.STATUS_TRUCKDUMP_UNCLAIMED

    def locate_product(self, row, session=None, vendor=None):
        """
        Try to locate the product represented by the given row.  Default
        behavior here, is to do a simple lookup on either ``Product.upc`` or
        ``Product.item_id``, depending on which is configured as your product
        key field.
        """
        if not session:
            session = orm.object_session(row)
        product_key = self.config.product_key()

        if product_key == 'upc':
            if row.upc:
                product = api.get_product_by_upc(session, row.upc)
                if product:
                    return product

        elif product_key == 'item_id':
            if row.item_id:
                product = api.get_product_by_item_id(session, row.item_id)
                if product:
                    return product

        # product key didn't work, but vendor item code just might
        if row.vendor_code:
            product = api.get_product_by_vendor_code(session, row.vendor_code,
                                                     vendor=vendor or row.batch.vendor)
            if product:
                return product

        # before giving up, let's do a lookup on alt codes too
        if row.item_entry:
            product = api.get_product_by_code(session, row.item_entry)
            if product:
                return product

    def transform_pack_to_unit(self, row):
        """
        Transform the given row, which is assumed to associate with a "pack"
        item, such that it associates with the "unit" item instead.
        """
        if not row.product:
            return
        if not row.product.is_pack_item():
            return

        assert row.batch.is_truck_dump_parent()

        # remove any existing claims for this (parent) row
        if row.claims:
            session = orm.object_session(row)
            del row.claims[:]
            # set temporary status for the row, if needed.  this is to help
            # with claiming logic below
            if row.status_code in (row.STATUS_TRUCKDUMP_PARTCLAIMED,
                                   row.STATUS_TRUCKDUMP_CLAIMED,
                                   row.STATUS_TRUCKDUMP_OVERCLAIMED):
                row.status_code = row.STATUS_TRUCKDUMP_UNCLAIMED
            session.flush()
            session.refresh(row)

        # pretty sure this is the only status we're expecting at this point...
        assert row.status_code == row.STATUS_TRUCKDUMP_UNCLAIMED

        # replace the row's product association
        pack = row.product
        unit = pack.unit
        row.product = unit
        row.item_id = unit.item_id
        row.upc = unit.upc

        # set new case quantity, per preferred cost
        cost = unit.cost_for_vendor(row.batch.vendor)
        row.case_quantity = (cost.case_size or 1) if cost else 1

        # must recalculate "units received" since those were for the pack item
        if row.units_received:
            row.units_received *= pack.pack_size

        # try to establish "claims" between parent and child(ren)
        self.make_truck_dump_claims_for_parent_row(row)

        # refresh the row itself, so product attributes will be updated
        self.refresh_row(row)

        # refresh status for the batch(es) proper, just in case this changed things
        self.refresh_batch_status(row.batch)
        for child in row.batch.truck_dump_children:
            self.refresh_batch_status(child)

    def make_truck_dump_claims_for_parent_row(self, row):
        """
        Try to establish all "truck dump claims" between parent and children,
        for the given parent row.
        """
        for child in row.batch.truck_dump_children:
            child_rows = [child_row for child_row in child.active_rows()
                          if child_row.product_uuid == row.product.uuid]
            if child_rows:
                self.make_truck_dump_claims(row, child_rows)
                if row.status_code not in (row.STATUS_TRUCKDUMP_UNCLAIMED,
                                           row.STATUS_TRUCKDUMP_PARTCLAIMED):
                    break

    def after_add_row(self, batch, row):
        if batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:

            # update "original" invoice total for batch
            if row.invoice_total is not None:
                batch.invoice_total = (batch.invoice_total or 0) + row.invoice_total

            # update "calculated" invoice totals for row, batch
            if row.invoice_unit_cost is None:
                row.invoice_total_calculated = None
            else:
                row.invoice_total_calculated = row.invoice_unit_cost * self.get_units_accounted_for(row)
            if row.invoice_total_calculated is not None:
                batch.invoice_total_calculated = (batch.invoice_total_calculated or 0) + row.invoice_total_calculated

    def refresh_row(self, row, initial=False):
        """
        Refreshing a row will A) assume that ``row.product`` is already set to
        a valid product, or else will attempt to locate the product, and B)
        update various other fields on the row (description, size, etc.)  to
        reflect the current product data.  It also will adjust the batch PO
        total per the row PO total.
        """
        batch = row.batch

        # first identify the product, or else we have nothing more to do
        product = row.product
        if not product:
            product = self.locate_product(row)
            if product:
                row.product = product
            else:
                row.status_code = row.STATUS_PRODUCT_NOT_FOUND
                return

        # update various (cached) product attributes for the row
        cost = product.cost_for_vendor(batch.vendor)
        row.upc = product.upc
        row.item_id = product.item_id
        row.brand_name = six.text_type(product.brand or '')
        row.description = product.description
        row.size = product.size
        if product.department:
            row.department_number = product.department.number
            row.department_name = product.department.name
        else:
            row.department_number = None
            row.department_name = None
        row.vendor_code = cost.code if cost else None

        # figure out the effective case quantity, and whether it differs with
        # what we previously had on file
        case_quantity_differs = False
        if cost and cost.case_size:
            if not row.case_quantity:
                row.case_quantity = cost.case_size
            elif row.case_quantity != cost.case_size:
                if batch.is_truck_dump_parent():
                    if batch.truck_dump_children_first:
                        # supposedly our case quantity came from a truck dump
                        # child row, which we assume to be authoritative
                        case_quantity_differs = True
                    else:
                        # truck dump has no children yet, which means we have
                        # no special authority for case quantity; therefore
                        # should treat master cost record as authority
                        row.case_quantity = cost.case_size
                else:
                    case_quantity_differs = True

        # determine PO / invoice unit cost if necessary
        if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING and row.po_unit_cost is None:
            row.po_unit_cost = self.get_unit_cost(row.product, batch.vendor)
        if batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING and row.invoice_unit_cost is None:
            row.invoice_unit_cost = row.po_unit_cost or (cost.unit_cost if cost else None)

        # all that's left should be setting status for the row...and that logic
        # will primarily depend on the 'mode' for this purchase batch

        if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
            row.status_code = row.STATUS_OK

        elif batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:

            # first check to see if we have *any* confirmed items
            if not (row.cases_received or row.units_received or
                    row.cases_damaged or row.units_damaged or
                    row.cases_expired or row.units_expired or
                    row.cases_mispick or row.units_mispick):

                # no, we do not have any confirmed items...

                # TODO: is this right? should row which ordered nothing just be removed?
                if batch.order_quantities_known and not (row.cases_ordered or row.units_ordered):
                    row.status_code = row.STATUS_OK
                # TODO: is this right? should out of stock just be a filter for
                # the user to specify, or should it affect status?
                elif row.out_of_stock:
                    row.status_code = row.STATUS_OUT_OF_STOCK
                else:
                    row.status_code = row.STATUS_INCOMPLETE

                # truck dump parent rows are also given status for that, which
                # reflects claimed vs. pending, i.e. child reconciliation
                if batch.is_truck_dump_parent():
                    row.truck_dump_status = row.STATUS_TRUCKDUMP_CLAIMED

            else: # we do have some confirmed items

                # primary status code for row should ideally reflect ordered
                # vs. received, although there are some exceptions
                # TODO: this used to prefer "case qty differs" and now i'm not
                # sure what the priority should be..perhaps config should say?
                if batch.order_quantities_known and (
                        self.get_units_shipped(row) != self.get_units_accounted_for(row)):
                    row.status_code = row.STATUS_ORDERED_RECEIVED_DIFFER
                elif case_quantity_differs:
                    row.status_code = row.STATUS_CASE_QUANTITY_DIFFERS
                    row.status_text = "batch has {} but master cost has {}".format(
                        repr(row.case_quantity), repr(cost.case_size))
                # TODO: is this right? should out of stock just be a filter for
                # the user to specify, or should it affect status?
                elif row.out_of_stock:
                    row.status_code = row.STATUS_OUT_OF_STOCK
                else:
                    row.status_code = row.STATUS_OK

                # truck dump parent rows are also given status for that, which
                # reflects claimed vs. pending, i.e. child reconciliation
                if batch.is_truck_dump_parent():
                    confirmed = self.get_units_confirmed(row)
                    claimed = self.get_units_claimed(row)
                    if claimed == confirmed:
                        row.truck_dump_status = row.STATUS_TRUCKDUMP_CLAIMED
                    elif not claimed:
                        row.truck_dump_status = row.STATUS_TRUCKDUMP_UNCLAIMED
                    elif claimed < confirmed:
                        row.truck_dump_status = row.STATUS_TRUCKDUMP_PARTCLAIMED
                    elif claimed > confirmed:
                        row.truck_dump_status = row.STATUS_TRUCKDUMP_OVERCLAIMED
                    else:
                        raise NotImplementedError

        else:
            raise NotImplementedError("can't refresh row for batch of mode: {}".format(
                self.enum.PURCHASE_BATCH_MODE.get(batch.mode, "unknown ({})".format(batch.mode))))

    def can_declare_credit(self, row, credit_type='received', cases=None, units=None, **kwargs):
        """
        This method should be used to validate a potential declaration of
        credit, i.e. call this before calling :meth:`declare_credit()`.  See
        the latter for call signature documentation, as they are the same.

        This method will use similar logic to confirm the proposed credit is
        valid, i.e. there is sufficient "received" quantity in place for it.
        """
        # make sure we have cases *or* units
        if not (cases or units):
            raise ValueError("must provide amount for cases *or* units")
        if cases and units:
            raise ValueError("must provide amount for cases *or* units (but not both)")
        if cases and cases < 0:
            raise ValueError("must provide *positive* amount for cases")
        if units and units < 0:
            raise ValueError("must provide *positive* amount for units")

        # make sure we have a (non-executed) receiving batch
        if row.batch.mode != self.enum.PURCHASE_BATCH_MODE_RECEIVING:
            raise NotImplementedError("receive_row() is only for receiving batches")
        if row.batch.executed:
            raise NotImplementedError("receive_row() is only for *non-executed* batches")

        if cases:
            if row.cases_received and row.cases_received >= cases:
                return True

            if row.units_received:
                units = cases * row.case_quantity
                if row.units_received >= units:
                    return True

        if units:
            if row.units_received and row.units_received >= units:
                return True

            if row.cases_received:
                cases = units // row.case_quantity
                if units % row.case_quantity:
                    cases += 1
                if row.cases_received >= cases:
                    return True

        raise ValueError("credit amount must be <= 'received' amount for the row")

    def declare_credit(self, row, credit_type='received', cases=None, units=None, **kwargs):
        """
        This method is similar in nature to :meth:`receive_row()`, although its
        goal is different.  Whereas ``receive_row()`` is concerned with "adding
        confirmed quantities" to the row, ``declare_credit()`` will instead
        "convert" some quantity which was previously "received" into one of the
        possible credit types.

        In other words if you have "received" 2 CS of a given product, but then
        while stocking it you discover 3 EA are damaged, then you would use
        this method to declare a credit like so::

           handler.declare_credit(row, credit_type='damaged', units=3)

        The received quantity for the row would go down by 3 EA, and its
        damaged quantity would go up by 3 EA.  The logic is able to handle
        "splitting" a case as necessary to accomplish this.

        Note that each call must specify *either* a (non-empty) ``cases`` or
        ``units`` value, but *not* both!

        :param rattail.db.model.batch.purchase.PurchaseBatchRow row: Batch row
           which is to be updated with the given receiving data.  The row must
           exist, i.e. this method will not create a new row for you.

        :param str credit_type: Must be one of the credit types which are
           "supported" according to the handler.  Possible types include:

           * ``'damaged'``
           * ``'expired'``
           * ``'mispick'``

        :param decimal.Decimal cases: Case quantity for the credit, if applicable.

        :param decimal.Decimal units: Unit quantity for the credit, if applicable.

        :param datetime.date expiration_date: Expiration date for the credit,
           if applicable.  Only used if ``credit_type='expired'``.
        """
        # make sure we have cases *or* units
        if not (cases or units):
            raise ValueError("must provide amount for cases *or* units")
        if cases and units:
            raise ValueError("must provide amount for cases *or* units (but not both)")
        if cases and cases < 0:
            raise ValueError("must provide *positive* amount for cases")
        if units and units < 0:
            raise ValueError("must provide *positive* amount for units")

        # make sure we have a (non-executed) receiving batch
        if row.batch.mode != self.enum.PURCHASE_BATCH_MODE_RECEIVING:
            raise NotImplementedError("receive_row() is only for receiving batches")
        if row.batch.executed:
            raise NotImplementedError("receive_row() is only for *non-executed* batches")

        if cases:
            if row.cases_received and row.cases_received >= cases:
                self.receive_row(row, mode='received', cases=-cases)
                self.receive_row(row, mode=credit_type, cases=cases)
                return

            if row.units_received:
                units = cases * row.case_quantity
                if row.units_received >= units:
                    self.receive_row(row, mode='received', units=-units)
                    self.receive_row(row, mode=credit_type, units=units)
                    return

        if units:
            if row.units_received and row.units_received >= units:
                self.receive_row(row, mode='received', units=-units)
                self.receive_row(row, mode=credit_type, units=units)
                return

            if row.cases_received:
                cases = units // row.case_quantity
                if units % row.case_quantity:
                    cases += 1
                if row.cases_received >= cases:
                    self.receive_row(row, mode='received', cases=-cases)
                    if (cases * row.case_quantity) > units:
                        self.receive_row(row, mode='received', units=cases * row.case_quantity - units)
                    self.receive_row(row, mode=credit_type, units=units)
                    return

        raise ValueError("credit amount must be <= 'received' amount for the row")

    def receive_row(self, row, mode='received', cases=None, units=None, **kwargs):
        """
        This method is arguably the workhorse of the whole process. Callers
        should invoke it as they receive input from the user during the
        receiving workflow.

        Each call to this method must include the row to be updated, as well as
        the details of the update.  These details should reflect "changes"
        which are to be made, as opposed to "final values" for the row.  In
        other words if a row already has ``cases_received == 1`` and the user
        is receiving a second case, this method should be called like so::

           handler.receive_row(row, mode='received', cases=1)

        The row will be updated such that ``cases_received == 2``; the main
        point here is that the caller should *not* specify ``cases=2`` because
        it is the handler's job to "apply changes" from the caller.  (If the
        caller speficies ``cases=2`` then the row would end up with
        ``cases_received == 3``.)

        For "undo" type adjustments, caller can just send a negative amount,
        and the handler will apply the changes as expected::

           handler.receive_row(row, mode='received', cases=-1)

        Note that each call must specify *either* a (non-empty) ``cases`` or
        ``units`` value, but *not* both!

        :param rattail.db.model.batch.purchase.PurchaseBatchRow row: Batch row
           which is to be updated with the given receiving data.  The row must
           exist, i.e. this method will not create a new row for you.

        :param str mode: Must be one of the receiving modes which are
           "supported" according to the handler.  Possible modes include:

           * ``'received'``
           * ``'damaged'``
           * ``'expired'``
           * ``'mispick'``

        :param decimal.Decimal cases: Case quantity for the update, if applicable.

        :param decimal.Decimal units: Unit quantity for the update, if applicable.

        :param datetime.date expiration_date: Expiration date for the update,
           if applicable.  Only used if ``mode='expired'``.

        This method exists mostly to consolidate the various logical steps which
        must be taken for each new receiving input from the user.  Under the hood
        it delegates to a few other methods:

        * :meth:`receiving_update_row_attrs()`
        * :meth:`receiving_update_row_credits()`
        * :meth:`receiving_update_row_children()`
        """
        # make sure we have cases *or* units
        if not (cases or units):
            raise ValueError("must provide amount for cases *or* units")
        if cases and units:
            raise ValueError("must provide amount for cases *or* units (but not both)")

        # make sure we have a (non-executed) receiving batch
        if row.batch.mode != self.enum.PURCHASE_BATCH_MODE_RECEIVING:
            raise NotImplementedError("receive_row() is only for receiving batches")
        if row.batch.executed:
            raise NotImplementedError("receive_row() is only for *non-executed* batches")

        # update the given row
        self.receiving_update_row_attrs(row, mode, cases, units)

        # update the given row's credits
        self.receiving_update_row_credits(row, mode, cases, units, **kwargs)

        # update the given row's "children" (if this is truck dump parent)
        self.receiving_update_row_children(row, mode, cases, units, **kwargs)

    def receiving_update_row_attrs(self, row, mode, cases, units):
        """
        Apply a receiving update to the row's attributes.

        Note that this should not be called directly; it is invoked as part of
        :meth:`receive_row()`.
        """
        batch = row.batch

        # add values as-is to existing case/unit amounts.  note
        # that this can sometimes give us negative values!  e.g. if
        # user scans 1 CS and then subtracts 2 EA, then we would
        # have 1 / -2 for our counts.  but we consider that to be
        # expected, and other logic must allow for the possibility
        if cases:
            setattr(row, 'cases_{}'.format(mode),
                    (getattr(row, 'cases_{}'.format(mode)) or 0) + cases)
        if units:
            setattr(row, 'units_{}'.format(mode),
                    (getattr(row, 'units_{}'.format(mode)) or 0) + units)

        # refresh row status etc.
        self.refresh_row(row)

        # update calculated invoice totals if normal received amounts
        if mode == 'received':
            # TODO: should round invoice amount to 2 places here?
            invoice_amount = 0
            if cases:
                invoice_amount += cases * row.case_quantity * row.invoice_unit_cost
            if units:
                invoice_amount += units * row.invoice_unit_cost
            row.invoice_total_calculated = (row.invoice_total_calculated or 0) + invoice_amount
            batch.invoice_total_calculated = (batch.invoice_total_calculated or 0) + invoice_amount

    def receiving_update_row_credits(self, row, mode, cases, units, **kwargs):
        """
        Apply a receiving update to the row's credits, if applicable.

        Note that this should not be called directly; it is invoked as part of
        :meth:`receive_row()`.
        """
        batch = row.batch

        # only certain modes should involve credits
        if mode not in ('damaged', 'expired', 'mispick'):
            return

        # TODO: need to add mispick support obviously
        if mode == 'mispick':
            raise NotImplementedError("mispick credits not yet supported")

        # TODO: must account for negative values here! i.e. remove credit in
        # some scenarios, perhaps using `kwargs` to find the match?
        if (cases and cases > 0) or (units and units > 0):
            positive = True
        else:
            positive = False
            raise NotImplementedError("TODO: add support for negative values when updating credits")

        # always make new credit; never aggregate
        credit = model.PurchaseBatchCredit()
        self.populate_credit(credit, row)
        credit.credit_type = mode
        credit.cases_shorted = cases or None
        credit.units_shorted = units or None

        # calculate credit total
        # TODO: should this leverage case cost if present?
        credit_units = self.get_units(credit.cases_shorted,
                                      credit.units_shorted,
                                      credit.case_quantity)
        credit.credit_total = credit_units * (credit.invoice_unit_cost or 0)

        # apply other attributes to credit, per caller kwargs
        credit.product_discarded = kwargs.get('discarded')
        if mode == 'expired':
            credit.expiration_date = kwargs.get('expiration_date')
        elif mode == 'mispick' and kwargs.get('mispick_product'):
            mispick_product = kwargs['mispick_product']
            credit.mispick_product = mispick_product
            credit.mispick_upc = mispick_product.upc
            if mispick_product.brand:
                credit.mispick_brand_name = mispick_product.brand.name
            credit.mispick_description = mispick_product.description
            credit.mispick_size = mispick_product.size

        # attach credit to row
        row.credits.append(credit)

    def populate_credit(self, credit, row):
        """
        Populate all basic attributes for the given credit, from the given row.
        """
        batch = row.batch

        credit.store = batch.store
        credit.vendor = batch.vendor
        credit.date_ordered = batch.date_ordered
        credit.date_shipped = batch.date_shipped
        credit.date_received = batch.date_received
        credit.invoice_number = batch.invoice_number
        credit.invoice_date = batch.invoice_date
        credit.product = row.product
        credit.upc = row.upc
        credit.vendor_item_code = row.vendor_code
        credit.brand_name = row.brand_name
        credit.description = row.description
        credit.size = row.size
        credit.department_number = row.department_number
        credit.department_name = row.department_name
        credit.case_quantity = row.case_quantity
        credit.invoice_line_number = row.invoice_line_number
        credit.invoice_case_cost = row.invoice_case_cost
        credit.invoice_unit_cost = row.invoice_unit_cost
        credit.invoice_total = row.invoice_total_calculated

    def receiving_update_row_children(self, row, mode, cases, units, **kwargs):
        """
        Apply a receiving update to the row's "children", if applicable.

        Note that this should not be called directly; it is invoked as part of
        :meth:`receive_row()`.

        This logic only applies to a "truck dump parent" row, since that is the
        only type which can have "children".  Also this logic is assumed only
        to apply if using the "children first" workflow.  If these criteria are
        not met then nothing is done.

        This method is ultimately responsible for updating "everything"
        (relevant) about the children of the given parent row.  This includes
        updating the child row(s) as well as the "claim" records used for
        reconciliation, as well as any child credit(s).  However most of the
        heavy lifting is done by :meth:`receiving_update_row_child()`.
        """
        batch = row.batch

        # updating row children is only applicable for truck dump parent, and
        # even then only if "children first" workflow
        if not batch.is_truck_dump_parent():
            return
        # TODO: maybe should just check for `batch.truck_dump_children` instead?
        if not batch.truck_dump_children_first:
            return

        # apply changes to child row(s) until we exhaust update quantities
        while cases or units:

            # find the "best match" child per current quantities, or quit if we
            # can no longer find any child match at all
            child_row = self.receiving_find_best_child_row(row, mode, cases, units)
            if not child_row:
                break

            # apply update to child, which should reduce our quantities
            before = cases, units
            cases, units = self.receiving_update_row_child(row, child_row, mode, cases, units, **kwargs)
            if (cases, units) == before:
                raise RuntimeError("infinite loop detected; aborting")

        # refresh parent row status
        self.refresh_row(row)

    def receiving_update_row_child(self, parent_row, child_row, mode, cases, units, **kwargs):
        """
        Update the given child row attributes, as well as the "claim" record
        which ties it to the parent, as well as any credit(s) which may apply.

        Ideally the child row can accommodate the "full" case/unit amounts
        given, but if not then it must do as much as it can.  Note that the
        child row should have been located via :meth:`receiving_find_best_child_row()`
        and therefore should be able to accommodate *something* at least.

        This method returns a 2-tuple of ``(cases, units)`` which reflect the
        amounts it was *not* able to claim (or relinquish, if incoming amounts
        are negative).  In other words these are the "leftovers" which still
        need to be dealt with somehow.
        """
        # were we given positive or negative values for the update?
        if (cases and cases > 0) or (units and units > 0):
            positive = True
        else:
            positive = False

        ##############################

        def update(cases, units):

            # update child claim
            claim = get_claim()
            if cases:
                setattr(claim, 'cases_{}'.format(mode),
                        (getattr(claim, 'cases_{}'.format(mode)) or 0) + cases)
            if units:
                setattr(claim, 'units_{}'.format(mode),
                        (getattr(claim, 'units_{}'.format(mode)) or 0) + units)
            # remove claim if now empty (should only happen if negative values?)
            if claim.is_empty():
                parent_row.claims.remove(claim)

            # update child row
            self.receiving_update_row_attrs(child_row, mode, cases, units)
            if cases:
                child_row.cases_shipped_claimed += cases
                child_row.cases_shipped_pending -= cases
            if units:
                child_row.units_shipped_claimed += units
                child_row.units_shipped_pending -= units

            # update child credit, if applicable
            self.receiving_update_row_credits(child_row, mode, cases, units, **kwargs)

        def get_claim():
            claims = [claim for claim in parent_row.claims
                      if claim.claiming_row is child_row]
            if claims:
                if len(claims) > 1:
                    raise ValueError("child row has too many claims on parent!")
                return claims[0]
            claim = model.PurchaseBatchRowClaim()
            claim.claiming_row = child_row
            parent_row.claims.append(claim)
            return claim

        ##############################

        # first we try to accommodate the full "as-is" amounts, if possible
        if positive:
            if cases and units:
                if child_row.cases_shipped_pending >= cases and child_row.units_shipped_pending >= units:
                    update(cases, units)
                    return 0, 0
            elif cases:
                if child_row.cases_shipped_pending >= cases:
                    update(cases, 0)
                    return 0, 0
            else: # units
                if child_row.units_shipped_pending >= units:
                    update(0, units)
                    return 0, 0
        else: # negative
            if cases and units:
                if child_row.cases_shipped_claimed >= -cases and child_row.units_shipped_claimed >= -units:
                    update(cases, units)
                    return 0, 0
            elif cases:
                if child_row.cases_shipped_claimed >= -cases:
                    update(cases, 0)
                    return 0, 0
            else: # units
                if child_row.units_shipped_claimed >= -units:
                    update(0, units)
                    return 0, 0

        # next we try a couple more variations on that theme, aiming for "as
        # much as possible, as simply as possible"
        if cases and units:
            if positive:
                if child_row.cases_shipped_pending >= cases:
                    update(cases, 0)
                    return 0, units
                if child_row.units_shipped_pending >= units:
                    update(0, units)
                    return cases, 0
            else: # negative
                if child_row.cases_shipped_claimed >= -cases:
                    update(cases, 0)
                    return 0, units
                if child_row.units_shipped_claimed >= -units:
                    update(0, units)
                    return cases, 0

        # okay then, try to (simply) use up any "child" quantities
        if positive:
            if cases and units and (child_row.cases_shipped_pending
                                    and child_row.units_shipped_pending):
                pending = (child_row.cases_shipped_pending,
                           child_row.units_shipped_pending)
                update(pending[0], pending[1])
                return cases - pending[0], units - pending[1]
            if cases and child_row.cases_shipped_pending:
                pending = child_row.cases_shipped_pending
                update(pending, 0)
                return cases - pending, 0
            if units and child_row.units_shipped_pending:
                pending = child_row.units_shipped_pending
                update(0, pending)
                return 0, units - pending
        else: # negative
            if cases and units and (child_row.cases_shipped_claimed
                                    and child_row.units_shipped_claimed):
                claimed = (child_row.cases_shipped_claimed,
                           child_row.units_shipped_claimed)
                update(-claimed[0], -claimed[1])
                return cases + claimed[0], units + claimed[1]
            if cases and child_row.cases_shipped_claimed:
                claimed = child_row.cases_shipped_claimed
                update(-claimed, 0)
                return cases + claimed, 0
            if units and child_row.units_shipped_claimed:
                claimed = child_row.units_shipped_claimed
                update(0, -claimed)
                return 0, units + claimed

        # looks like we're gonna have to split some cases, one way or another
        if parent_row.case_quantity != child_row.case_quantity:
            raise NotImplementedError("cannot split case when parent/child disagree about size")
        if positive:
            if cases and child_row.units_shipped_pending:
                if child_row.units_shipped_pending >= parent_row.case_quantity:
                    unit_cases = child_row.units_shipped_pending // parent_row.case_quantity
                    if unit_cases >= cases:
                        update(0, cases * parent_row.case_quantity)
                        return 0, units
                    else: # unit_cases < cases
                        update(0, unit_cases * parent_row.case_quantity)
                        return cases - unit_cases, units
                else: # units_pending < case_size
                    pending = child_row.units_shipped_pending
                    update(0, pending)
                    return (cases - 1,
                            (units or 0) + parent_row.case_quantity - pending)
            if units and child_row.cases_shipped_pending:
                if units >= parent_row.case_quantity:
                    unit_cases = units // parent_row.case_quantity
                    if unit_cases <= child_row.cases_shipped_pending:
                        update(unit_cases, 0)
                        return 0, units - (unit_cases * parent_row.case_quantity)
                    else: # unit_cases > cases_pending
                        pending = child_row.cases_shipped_pending
                        update(pending, 0)
                        return 0, units - (pending * parent_row.case_quantity)
                else: # units < case_size
                    update(0, units)
                    return 0, 0
        else: # negative
            if cases and child_row.units_shipped_claimed:
                if child_row.units_shipped_claimed >= parent_row.case_quantity:
                    unit_cases = child_row.units_shipped_claimed // parent_row.case_quantity
                    if unit_cases >= -cases:
                        update(0, cases * parent_row.case_quantity)
                        return 0, units
                    else: # unit_cases < -cases
                        update(0, -unit_cases * parent_row.case_quantity)
                        return cases + unit_cases, units
                else: # units_claimed < case_size
                    claimed = child_row.units_shipped_claimed
                    update(0, -claimed)
                    return (cases + 1,
                            (units or 0) - parent_row.case_quantity + claimed)
            if units and child_row.cases_shipped_claimed:
                if -units >= parent_row.case_quantity:
                    unit_cases = -units // parent_row.case_quantity
                    if unit_cases <= child_row.cases_shipped_claimed:
                        update(-unit_cases, 0)
                        return 0, units + (unit_cases * parent_row.case_quantity)
                    else: # unit_cases > cases_claimed
                        claimed = child_row.cases_shipped_claimed
                        update(-claimed, 0)
                        return 0, units + (claimed * parent_row.case_quantity)
                else: # -units < case_size
                    update(0, units)
                    return 0, 0

        # TODO: this should theoretically never happen; should log/raise error?
        log.warning("unable to claim/relinquish any case/unit amounts for child row: %s", child_row)
        return cases, units

    def receiving_find_best_child_row(self, row, mode, cases, units):
        """
        Locate and return the "best match" child row, for the given parent row
        and receiving update details.  The idea here is that the parent row
        will represent the "receiving" side of things, whereas the child row
        will be the "ordering" side.

        For instance if the update is for say, "received 2 CS" and there are
        two child rows, one of which is for 1 CS and the other 2 CS, the latter
        will be returned.  This logic is capable of "splitting" a case where
        necessary, in order to find a partial match etc.
        """
        parent_row = row
        parent_batch = parent_row.batch

        if not (cases or units):
            raise ValueError("must provide amount for cases and/or units")

        if cases and units and (
                (cases > 0 and units < 0) or (cases < 0 and units > 0)):
            raise NotImplementedError("not sure how to handle mixed pos/neg for case/unit amounts")

        # were we given positive or negative values for the update?
        if (cases and cases > 0) or (units and units > 0):
            positive = True
        else:
            positive = False

        # first we collect all potential child rows
        all_child_rows = []
        for child_batch in parent_batch.truck_dump_children:

            # match on exact product if possible, otherwise must match on upc etc.
            if parent_row.product:
                child_rows = [child_row for child_row in child_batch.active_rows()
                              if child_row.product_uuid == parent_row.product.uuid]
            else:
                # note that we only want to match child rows which have *no* product ref
                # TODO: should consult config to determine which product key to match on
                child_rows = [child_row for child_row in child_batch.active_rows()
                              if not child_row.product_uuid and child_row.upc == parent_row.upc]

            for child_row in child_rows:

                # for each child row we also calculate "claimed" vs. "pending" amounts

                # cases_ordered
                child_row.cases_shipped_claimed = sum([(claim.cases_received or 0)
                                                       + (claim.cases_damaged or 0)
                                                       + (claim.cases_expired or 0)
                                                       for claim in child_row.truck_dump_claims])
                child_row.cases_shipped_pending = (child_row.cases_ordered or 0) - child_row.cases_shipped_claimed

                # units_ordered
                child_row.units_shipped_claimed = sum([(claim.units_received or 0)
                                                       + (claim.units_damaged or 0)
                                                       + (claim.units_expired or 0)
                                                       for claim in child_row.truck_dump_claims])
                child_row.units_shipped_pending = (child_row.units_ordered or 0) - child_row.units_shipped_claimed

                # maybe account for split cases
                if child_row.units_shipped_pending < 0:
                    split_cases = -child_row.units_shipped_pending // child_row.case_quantity
                    if -child_row.units_shipped_pending % child_row.case_quantity:
                        split_cases += 1
                    if split_cases > child_row.cases_shipped_pending:
                        raise ValueError("too many cases have been split?")
                    child_row.cases_shipped_pending -= split_cases
                    child_row.units_shipped_pending += split_cases * child_row.case_quantity

                all_child_rows.append(child_row)

        def sortkey(row):
            if positive:
                return self.get_units(row.cases_shipped_pending,
                                      row.units_shipped_pending,
                                      row.case_quantity)
            else: # negative
                return self.get_units(row.cases_shipped_claimed,
                                      row.units_shipped_claimed,
                                      row.case_quantity)

        # sort child rows such that smallest (relevant) quantities come first;
        # idea being we would prefer the "least common denominator" to match
        all_child_rows.sort(key=sortkey)

        # first try to find an exact match
        for child_row in all_child_rows:
            if cases and units:
                if positive:
                    if child_row.cases_shipped_pending == cases and child_row.units_shipped_pending == units:
                        return child_row
                else: # negative
                    if child_row.cases_shipped_claimed == cases and child_row.units_shipped_claimed == units:
                        return child_row
            elif cases:
                if positive:
                    if child_row.cases_shipped_pending == cases:
                        return child_row
                else: # negative
                    if child_row.cases_shipped_claimed == cases:
                        return child_row
            else: # units
                if positive:
                    if child_row.units_shipped_pending == units:
                        return child_row
                else: # negative
                    if child_row.units_shipped_claimed == units:
                        return child_row

        # next we try to find the "first" (smallest) match which satisfies, but
        # which does so *without* having to split up any cases
        for child_row in all_child_rows:
            if cases and units:
                if positive:
                    if child_row.cases_shipped_pending >= cases and child_row.units_shipped_pending >= units:
                        return child_row
                else: # negative
                    if child_row.cases_shipped_claimed >= -cases and child_row.units_shipped_claimed >= -units:
                        return child_row
            elif cases:
                if positive:
                    if child_row.cases_shipped_pending >= cases:
                        return child_row
                else: # negative
                    if child_row.cases_shipped_claimed >= -cases:
                        return child_row
            else: # units
                if positive:
                    if child_row.units_shipped_pending >= units:
                        return child_row
                else: # negative
                    if child_row.units_shipped_claimed >= -units:
                        return child_row

        # okay, we're getting desperate now; let's start splitting cases and
        # may the first possible match (which fully satisfies) win...
        incoming_units = self.get_units(cases, units, parent_row.case_quantity)
        for child_row in all_child_rows:
            if positive:
                pending_units = self.get_units(child_row.cases_shipped_pending,
                                               child_row.units_shipped_pending,
                                               child_row.case_quantity)
                if pending_units >= incoming_units:
                    return child_row
            else: # negative
                claimed_units = self.get_units(child_row.cases_shipped_claimed,
                                               child_row.units_shipped_claimed,
                                               child_row.case_quantity)
                if claimed_units >= -incoming_units:
                    return child_row

        # and now we're even more desperate.  at this point no child row can
        # fully (by itself) accommodate the update at hand, which means we must
        # look for the first child which can accommodate anything at all, and
        # settle for the partial match.  note that we traverse the child row
        # list *backwards* here, hoping for the "biggest" match
        for child_row in reversed(all_child_rows):
            if positive:
                if child_row.cases_shipped_pending or child_row.units_shipped_pending:
                    return child_row
            else: # negative
                if child_row.cases_shipped_claimed or child_row.units_shipped_claimed:
                    return child_row

    def remove_row(self, row):
        """
        This handler does not simply mark the row "removed" but will instead
        delete the row outright.  It additionally will update certain (PO,
        invoice) totals on the batch.
        """
        session = orm.object_session(row)
        batch = row.batch

        if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
            if row.po_total:
                batch.po_total -= row.po_total

        elif batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
            if row.invoice_total_calculated:
                batch.invoice_total_calculated -= row.invoice_total_calculated

        session.delete(row)
        session.flush()
        self.refresh_batch_status(batch)

    def get_unit_cost(self, product, vendor):
        """
        Must return the PO unit cost for the given product, from the given vendor.
        """
        cost = product.cost_for_vendor(vendor) or product.cost
        if cost:
            return cost.unit_cost

    def get_units(self, cases, units, case_quantity):
        case_quantity = case_quantity or 1
        return (units or 0) + case_quantity * (cases or 0)

    def get_units_ordered(self, row, case_quantity=None):
        case_quantity = case_quantity or row.case_quantity or 1
        return self.get_units(row.cases_ordered, row.units_ordered, case_quantity)

    def get_units_shipped(self, row, case_quantity=None):
        case_quantity = case_quantity or row.case_quantity or 1
        return self.get_units(row.cases_shipped, row.units_shipped, case_quantity)

    def get_units_received(self, row, case_quantity=None):
        case_quantity = case_quantity or row.case_quantity or 1
        return self.get_units(row.cases_received, row.units_received, case_quantity)

    def get_units_damaged(self, row, case_quantity=None):
        case_quantity = case_quantity or row.case_quantity or 1
        return self.get_units(row.cases_damaged, row.units_damaged, case_quantity)

    def get_units_expired(self, row, case_quantity=None):
        case_quantity = case_quantity or row.case_quantity or 1
        return self.get_units(row.cases_expired, row.units_expired, case_quantity)

    def get_units_confirmed(self, row, case_quantity=None):
        received = self.get_units_received(row, case_quantity=case_quantity)
        damaged = self.get_units_damaged(row, case_quantity=case_quantity)
        expired = self.get_units_expired(row, case_quantity=case_quantity)
        return received + damaged + expired

    def get_units_mispick(self, row, case_quantity=None):
        case_quantity = case_quantity or row.case_quantity or 1
        return self.get_units(row.cases_mispick, row.units_mispick, case_quantity)

    def get_units_accounted_for(self, row, case_quantity=None):
        confirmed = self.get_units_confirmed(row, case_quantity=case_quantity)
        mispick = self.get_units_mispick(row, case_quantity=case_quantity)
        return confirmed + mispick

    def get_units_shorted(self, obj, case_quantity=None):
        case_quantity = case_quantity or obj.case_quantity or 1
        if hasattr(obj, 'cases_shorted'):
            # obj is really a credit
            return self.get_units(obj.cases_shorted, obj.units_shorted, case_quantity)
        else:
            # obj is a row, so sum the credits
            return sum([self.get_units(credit.cases_shorted, credit.units_shorted, case_quantity)
                        for credit in obj.credits])

    def get_units_claimed(self, row, case_quantity=None):
        """
        Returns the total number of units which are "claimed" by child rows,
        for the given truck dump parent row.
        """
        claimed = 0
        for claim in row.claims:
            # prefer child row's notion of case quantity, over parent row
            case_qty = case_quantity or claim.claiming_row.case_quantity or row.case_quantity
            claimed += self.get_units_confirmed(claim, case_quantity=case_qty)
        return claimed

    def get_units_claimed_received(self, row, case_quantity=None):
        return sum([self.get_units_received(claim, case_quantity=row.case_quantity)
                    for claim in row.claims])

    def get_units_claimed_damaged(self, row, case_quantity=None):
        return sum([self.get_units_damaged(claim, case_quantity=row.case_quantity)
                    for claim in row.claims])

    def get_units_claimed_expired(self, row, case_quantity=None):
        return sum([self.get_units_expired(claim, case_quantity=row.case_quantity)
                    for claim in row.claims])

    def get_units_available(self, row, case_quantity=None):
        confirmed = self.get_units_confirmed(row, case_quantity=case_quantity)
        claimed = self.get_units_claimed(row, case_quantity=case_quantity)
        return confirmed - claimed

    def auto_receive_all_items(self, batch, progress=None):
        """
        Automatically "receive" all items for the given batch.  Meant for
        development purposes only!
        """
        if self.config.production():
            raise NotImplementedError("Feature is not meant for production use.")

        def receive(row, i):

            # auto-receive whatever is left
            cases, units = self.calculate_pending(row)
            if cases:
                self.receive_row(row, mode='received', cases=cases)
            if units:
                self.receive_row(row, mode='received', units=units)

        self.progress_loop(receive, batch.active_rows(), progress,
                           message="Auto-receiving all items")

        self.refresh(batch, progress=progress)

    def update_order_counts(self, purchase, progress=None):

        def update(item, i):
            if item.product:
                inventory = item.product.inventory or model.ProductInventory(product=item.product)
                inventory.on_order = (inventory.on_order or 0) + (item.units_ordered or 0) + (
                    (item.cases_ordered or 0) * (item.case_quantity or 1))

        self.progress_loop(update, purchase.items, progress,
                           message="Updating inventory counts")

    def update_receiving_inventory(self, purchase, consume_on_order=True, progress=None):

        def update(item, i):
            if item.product:
                inventory = item.product.inventory or model.ProductInventory(product=item.product)
                count = (item.units_received or 0) + (item.cases_received or 0) * (item.case_quantity or 1)
                if count:
                    if consume_on_order:
                        if (inventory.on_order or 0) < count:
                            raise RuntimeError("Received {} units for {} but it only had {} on order".format(
                                count, item.product, inventory.on_order or 0))
                        inventory.on_order -= count
                    inventory.on_hand = (inventory.on_hand or 0) + count

        self.progress_loop(update, purchase.items, progress,
                           message="Updating inventory counts")

    def why_not_execute(self, batch):
        """
        This method should return a string indicating the reason why the given
        batch should not be considered executable.  By default it returns
        ``None`` which means the batch *is* to be considered executable.

        Note that it is assumed the batch has not already been executed, since
        execution is globally prevented for such batches.
        """
        # not all receiving batches are executable
        if batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:

            if batch.is_truck_dump_parent() and batch.truck_dump_status != batch.STATUS_TRUCKDUMP_CLAIMED:
                return ("Can't execute a Truck Dump (parent) batch until "
                        "it has been fully claimed by children")

            if batch.is_truck_dump_child():
                return ("Can't directly execute batch which is child of a truck dump "
                        "(must execute truck dump instead)")

    def execute(self, batch, user, progress=None):
        """
        Default behavior for executing a purchase batch will create a new
        purchase, by invoking :meth:`make_purchase()`.
        """
        session = orm.object_session(batch)

        if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
            purchase = self.make_purchase(batch, user, progress=progress)
            self.update_order_counts(purchase, progress=progress)
            return purchase

        elif batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
            if not batch.date_received:
                batch.date_received = localtime(self.config).date()
            if self.allow_truck_dump and batch.is_truck_dump_parent():
                self.execute_truck_dump(batch, user, progress=progress)
                return True
            else:
                with session.no_autoflush:
                    return self.receive_purchase(batch, progress=progress)

        elif batch.mode == self.enum.PURCHASE_BATCH_MODE_COSTING:
            # TODO: finish this...
            # with session.no_autoflush:
            #     return self.cost_purchase(batch, progress=progress)
            purchase = batch.purchase
            purchase.invoice_date = batch.invoice_date
            purchase.status = self.enum.PURCHASE_STATUS_COSTED
            return purchase

        assert False

    def execute_truck_dump(self, batch, user, progress=None):
        now = make_utc()
        for child in batch.truck_dump_children:
            if not self.execute(child, user, progress=progress):
                raise RuntimeError("Failed to execute child batch: {}".format(child))
            child.executed = now
            child.executed_by = user

    def make_credits(self, batch, progress=None):
        """
        Make all final credit records for the given batch.  Meant to be called
        as part of the batch execution process.
        """
        session = orm.object_session(batch)
        mapper = orm.class_mapper(model.PurchaseBatchCredit)
        date_received = batch.date_received
        if not date_received:
            date_received = localtime(self.config).date()

        def add_credits(row, i):

            # basically "clone" existing credits from batch row
            for batch_credit in row.credits:
                credit = model.PurchaseCredit()
                for prop in mapper.iterate_properties:
                    if isinstance(prop, orm.ColumnProperty) and hasattr(credit, prop.key):
                        setattr(credit, prop.key, getattr(batch_credit, prop.key))
                credit.status = self.enum.PURCHASE_CREDIT_STATUS_NEW
                if not credit.date_received:
                    credit.date_received = date_received
                session.add(credit)

            # maybe create "missing" credits for items not accounted for
            if not row.out_of_stock:
                cases, units = self.calculate_pending(row)
                if cases or units:
                    credit = model.PurchaseCredit()
                    self.populate_credit(credit, row)
                    credit.credit_type = 'missing'
                    credit.cases_shorted = cases or None
                    credit.units_shorted = units or None

                    # calculate credit total
                    # TODO: should this leverage case cost if present?
                    credit_units = self.get_units(credit.cases_shorted,
                                                  credit.units_shorted,
                                                  credit.case_quantity)
                    credit.credit_total = credit_units * (credit.invoice_unit_cost or 0)

                    credit.status = self.enum.PURCHASE_CREDIT_STATUS_NEW
                    if not credit.date_received:
                        credit.date_received = date_received
                    session.add(credit)

        return self.progress_loop(add_credits, batch.active_rows(), progress,
                                  message="Creating purchase credits")

    def calculate_pending(self, row):
        """
        Calculate the "pending" case and unit amounts for the given row.  This
        essentially is the difference between "ordered" and "confirmed",
        e.g. if a row has ``cases_ordered == 2`` and ``cases_received == 1``
        then it is considered to have "1 pending case".

        Note that this method *is* aware of the "split cases" problem, and will
        adjust the pending amounts if any split cases are detected.

        :returns: A 2-tuple of ``(cases, units)`` pending amounts.
        """
        # calculate remaining cases, units
        cases_confirmed = ((row.cases_received or 0)
                           + (row.cases_damaged or 0)
                           + (row.cases_expired or 0))
        cases_pending = (row.cases_ordered or 0) - cases_confirmed
        units_confirmed = ((row.units_received or 0)
                           + (row.units_damaged or 0)
                           + (row.units_expired or 0))
        units_pending = (row.units_ordered or 0) - units_confirmed

        # maybe account for split cases
        if units_pending < 0:
            split_cases = -units_pending // row.case_quantity
            if -units_pending % row.case_quantity:
                split_cases += 1
            if split_cases > cases_pending:
                raise ValueError("too many cases have been split?")
            cases_pending -= split_cases
            units_pending += split_cases * row.case_quantity

        return cases_pending, units_pending

    def make_purchase(self, batch, user, progress=None):
        """
        Effectively clones the given batch, creating a new Purchase in the
        Rattail system.
        """
        session = orm.object_session(batch)
        purchase = model.Purchase()

        # TODO: should be smarter and only copy certain fields here
        skip_fields = [
            'date_received',
        ]
        for prop in orm.object_mapper(batch).iterate_properties:
            if prop.key in skip_fields:
                continue
            if hasattr(purchase, prop.key):
                setattr(purchase, prop.key, getattr(batch, prop.key))

        def clone(row, i):
            item = model.PurchaseItem()
            # TODO: should be smarter and only copy certain fields here
            for prop in orm.object_mapper(row).iterate_properties:
                if hasattr(item, prop.key):
                    setattr(item, prop.key, getattr(row, prop.key))
            purchase.items.append(item)

        with session.no_autoflush:
            self.progress_loop(clone, batch.active_rows(), progress,
                               message="Creating purchase items")

        purchase.created = make_utc()
        purchase.created_by = user
        purchase.status = self.enum.PURCHASE_STATUS_ORDERED
        session.add(purchase)
        batch.purchase = purchase
        return purchase

    def receive_purchase(self, batch, progress=None):
        """
        Update the purchase for the given batch, to indicate received status.
        """
        session = orm.object_session(batch)
        purchase = batch.purchase
        if not purchase:
            batch.purchase = purchase = model.Purchase()

            # TODO: should be smarter and only copy certain fields here
            skip_fields = [
                'uuid',
                'date_received',
            ]
            with session.no_autoflush:
                for prop in orm.object_mapper(batch).iterate_properties:
                    if prop.key in skip_fields:
                        continue
                    if hasattr(purchase, prop.key):
                        setattr(purchase, prop.key, getattr(batch, prop.key))

        purchase.invoice_number = batch.invoice_number
        purchase.invoice_date = batch.invoice_date
        purchase.invoice_total = batch.invoice_total_calculated
        purchase.date_received = batch.date_received

        # determine which fields we'll copy when creating new purchase item
        copy_fields = []
        for prop in orm.class_mapper(model.PurchaseItem).iterate_properties:
            if hasattr(model.PurchaseBatchRow, prop.key):
                copy_fields.append(prop.key)

        def update(row, i):
            item = row.item
            if not item:
                row.item = item = model.PurchaseItem()
                for field in copy_fields:
                    setattr(item, field, getattr(row, field))
                purchase.items.append(item)

            item.cases_received = row.cases_received
            item.units_received = row.units_received
            item.cases_damaged = row.cases_damaged
            item.units_damaged = row.units_damaged
            item.cases_expired = row.cases_expired
            item.units_expired = row.units_expired
            item.invoice_line_number = row.invoice_line_number
            item.invoice_case_cost = row.invoice_case_cost
            item.invoice_unit_cost = row.invoice_unit_cost
            item.invoice_total = row.invoice_total_calculated

        with session.no_autoflush:
            self.progress_loop(update, batch.active_rows(), progress,
                               message="Updating purchase line items")

        purchase.status = self.enum.PURCHASE_STATUS_RECEIVED
        return purchase

    def clone_row(self, oldrow):
        newrow = super(PurchaseBatchHandler, self).clone_row(oldrow)

        for oldcredit in oldrow.credits:
            newcredit = model.PurchaseBatchCredit()
            self.copy_credit_attributes(oldcredit, newcredit)
            newrow.credits.append(newcredit)

        return newrow

    def copy_credit_attributes(self, source_credit, target_credit):
        mapper = orm.class_mapper(model.PurchaseBatchCredit)
        for prop in mapper.iterate_properties:
            if prop.key not in ('uuid', 'row_uuid'):
                if isinstance(prop, orm.ColumnProperty):
                    setattr(target_credit, prop.key, getattr(source_credit, prop.key))
