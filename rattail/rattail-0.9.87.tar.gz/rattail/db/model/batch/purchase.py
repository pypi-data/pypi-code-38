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
Models for purchase order batches
"""

from __future__ import unicode_literals, absolute_import

import six
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr

from rattail.db.model import (Base, BatchMixin, BatchRowMixin,
                              PurchaseBase, PurchaseItemBase, PurchaseCreditBase,
                              Purchase, PurchaseItem)
from rattail.db.core import uuid_column, filename_column


class PurchaseBatch(BatchMixin, PurchaseBase, Base):
    """
    Hopefully generic batch used for entering new purchases into the system, etc.?
    """
    batch_key = 'purchase'
    __tablename__ = 'purchase_batch'
    __batchrow_class__ = 'PurchaseBatchRow'
    model_title = "Purchasing Batch"
    model_title_plural = "Purchasing Batches"

    @declared_attr
    def __table_args__(cls):
        return cls.__batch_table_args__() + cls.__purchase_table_args__() + (
            sa.ForeignKeyConstraint(['purchase_uuid'], ['purchase.uuid'], name='purchase_batch_fk_purchase'),
            sa.ForeignKeyConstraint(['truck_dump_batch_uuid'], ['purchase_batch.uuid'], name='purchase_batch_fk_truck_dump_batch', use_alter=True),
        )

    STATUS_OK                   = 1
    STATUS_UNKNOWN_PRODUCT      = 2
    STATUS_TRUCKDUMP_UNCLAIMED  = 3
    STATUS_TRUCKDUMP_CLAIMED    = 4
    STATUS_UNKNOWN_COSTS        = 5

    STATUS = {
        STATUS_OK                       : "ok",
        STATUS_UNKNOWN_PRODUCT          : "has unknown product(s)",
        STATUS_UNKNOWN_COSTS            : "has unknown product cost(s)",
        STATUS_TRUCKDUMP_UNCLAIMED      : "not yet fully claimed",
        STATUS_TRUCKDUMP_CLAIMED        : "fully claimed by child(ren)",
    }

    purchase_uuid = sa.Column(sa.String(length=32), nullable=True)

    purchase = orm.relationship(
        Purchase,
        doc="""
        Reference to the purchase with which the batch is associated.  May be
        null, e.g. in the case of a "new purchase" batch.
        """,
        backref=orm.backref(
            'batches',
            order_by='PurchaseBatch.id',
            doc="""
            List of batches associated with the purchase.
            """))

    mode = sa.Column(sa.Integer(), nullable=False, doc="""
    Numeric "mode" for the purchase batch, to indicate new/receiving etc.
    """)

    invoice_file = filename_column(doc="Base name for the associated invoice file, if any.")

    invoice_parser_key = sa.Column(sa.String(length=100), nullable=True, doc="""
    The key of the parser used to read the contents of the invoice file.
    """)

    order_quantities_known = sa.Column(sa.Boolean(), nullable=True, doc="""
    Flag indicating whether the order quantities were known at time of batch
    creation / population.  Really this is only used for batches of 'receiving'
    mode, to present a slightly different UI if order quantities were (not) known.
    """)

    po_total_calculated = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Calculated PO total, per quantity received thus far (if applicable).
    """)

    invoice_total_calculated = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Calculated invoice total, per quantity received thus far (if applicable).
    """)

    truck_dump = sa.Column(sa.Boolean(), nullable=True, default=False, doc="""
    Flag indicating whether a "receiving" batch is of the "truck dump"
    persuasion, i.e.  it does not correspond to a single purchase order but
    rather is assumed to represent multiple orders.
    """)

    truck_dump_children_first = sa.Column(sa.Boolean(), nullable=True, default=False, doc="""
    If batch is a "truck dump parent", this flag indicates whether its
    "children" are to be attached *first* as opposed to *last*.  If the flag is
    true, all children must be attached prior to the receiving process.  If
    flag is false, receiving must happen first, and then all children attached
    at the end.
    """)

    truck_dump_ready = sa.Column(sa.Boolean(), nullable=True, default=False, doc="""
    If batch is a "truck dump parent", this flag indicates whether it is
    "ready" for the actual receiving process.  If children are to be attached
    first, this flag should not be set until all children are attached.  If
    children are last, this flag should be set immediately upon batch creation.
    """)

    truck_dump_status = sa.Column(sa.Integer(), nullable=True, doc="""
    Truck dump status code for the row.  Only relevant for truck dump parent
    batches.  Indicates whether this parent has been fully claimed by children
    yet, etc.
    """)

    truck_dump_batch_uuid = sa.Column(sa.String(length=32), nullable=True)
    truck_dump_batch = orm.relationship(
        'PurchaseBatch',
        remote_side='PurchaseBatch.uuid',
        doc="""
        Reference to the "truck dump" receiving batch, for which the current
        batch represents a single invoice which partially "consumes" the truck
        dump.
        """,
        backref=orm.backref(
            'truck_dump_children',
            order_by='PurchaseBatch.id',
            doc="""
            List of batches which are "children" of the current batch, which is
            assumed to be a truck dump.
            """))

    def is_truck_dump_parent(self):
        """
        Returns boolean indicating whether or not the batch is a "truck dump"
        parent.
        """
        if self.truck_dump:
            return True
        return False

    def is_truck_dump_child(self):
        """
        Returns boolean indicating whether or not the batch is a "truck dump"
        child.
        """
        if self.truck_dump_batch:
            return True
        return False

    def is_truck_dump_related(self):
        """
        Returns boolean indicating whether or not the batch is associated with
        a "truck dump" in any way, i.e. is a parent or child of such.
        """
        if self.is_truck_dump_parent():
            return True
        if self.is_truck_dump_child():
            return True
        return False


class PurchaseBatchRow(BatchRowMixin, PurchaseItemBase, Base):
    """
    Row of data within a purchase batch.
    """
    __tablename__ = 'purchase_batch_row'
    __batch_class__ = PurchaseBatch

    @declared_attr
    def __table_args__(cls):
        return cls.__batchrow_table_args__() + cls.__purchaseitem_table_args__() + (
            sa.ForeignKeyConstraint(['item_uuid'], ['purchase_item.uuid'], name='purchase_batch_row_fk_item'),
        )

    STATUS_OK                           = 1
    STATUS_PRODUCT_NOT_FOUND            = 2
    STATUS_COST_NOT_FOUND               = 3
    STATUS_CASE_QUANTITY_UNKNOWN        = 4
    STATUS_INCOMPLETE                   = 5
    STATUS_ORDERED_RECEIVED_DIFFER      = 6
    STATUS_TRUCKDUMP_UNCLAIMED          = 7
    STATUS_TRUCKDUMP_CLAIMED            = 8
    STATUS_TRUCKDUMP_OVERCLAIMED        = 9
    STATUS_CASE_QUANTITY_DIFFERS        = 10
    STATUS_TRUCKDUMP_PARTCLAIMED        = 11
    STATUS_OUT_OF_STOCK                 = 12

    STATUS = {
        STATUS_OK                       : "ok",
        STATUS_PRODUCT_NOT_FOUND        : "product not found",
        STATUS_COST_NOT_FOUND           : "product found but not cost",
        STATUS_CASE_QUANTITY_UNKNOWN    : "case quantity not known",
        STATUS_CASE_QUANTITY_DIFFERS    : "case quantity differs",
        STATUS_INCOMPLETE               : "incomplete",
        STATUS_ORDERED_RECEIVED_DIFFER  : "shipped / received differ",
        STATUS_TRUCKDUMP_UNCLAIMED      : "not claimed by any child(ren)",
        STATUS_TRUCKDUMP_PARTCLAIMED    : "partially claimed by child(ren)",
        STATUS_TRUCKDUMP_CLAIMED        : "fully claimed by child(ren)",
        STATUS_TRUCKDUMP_OVERCLAIMED    : "OVER claimed by child(ren)",
        STATUS_OUT_OF_STOCK             : "out of stock",
    }

    item_entry = sa.Column(sa.String(length=20), nullable=True, doc="""
    Raw entry value, as obtained from the initial data source, and which is
    used to locate the product within the system.  This raw value is preserved
    in case the initial lookup fails and a refresh must attempt further
    lookup(s) later.  Only used by certain batch handlers in practice.
    """)

    item_uuid = sa.Column(sa.String(length=32), nullable=True)

    item = orm.relationship(
        PurchaseItem,
        doc="""
        Reference to the purchase item with which the batch row is associated.
        May be null, e.g. in the case of a "new purchase" batch.
        """)

    po_total_calculated = sa.Column(sa.Numeric(precision=7, scale=2), nullable=True, doc="""
    Calculated total cost for line item, per quantity received thus far.  See
    also :attr:`po_total`.
    """)

    invoice_total_calculated = sa.Column(sa.Numeric(precision=7, scale=2), nullable=True, doc="""
    Calculated total cost for line item, per quantity received thus far.  See
    also :attr:`invoice_total`.
    """)

    truck_dump_status = sa.Column(sa.Integer(), nullable=True, doc="""
    Truck dump status code for the row.  Only relevant for truck dump parent
    batches.  Indicates whether this parent row has been fully claimed by
    children yet, etc.
    """)


class PurchaseBatchRowClaim(Base):
    """
    Represents the connection between a row(s) from a truck dump batch, and the
    corresponding "child" batch row which claims it, as well as the claimed
    quantities etc.
    """
    __tablename__ = 'purchase_batch_row_claim'
    __table_args__ = (
        sa.ForeignKeyConstraint(['claiming_row_uuid'], ['purchase_batch_row.uuid'], name='purchase_batch_row_claim_fk_claiming_row'),
        sa.ForeignKeyConstraint(['claimed_row_uuid'], ['purchase_batch_row.uuid'], name='purchase_batch_row_claim_fk_claimed_row'),
    )

    uuid = uuid_column()

    claiming_row_uuid = sa.Column(sa.String(length=32), nullable=False)
    claiming_row = orm.relationship(
        PurchaseBatchRow,
        foreign_keys='PurchaseBatchRowClaim.claiming_row_uuid',
        doc="""
        Reference to the "child" row which is claiming some row from a truck
        dump batch.
        """,
        backref=orm.backref(
            'truck_dump_claims',
            cascade='all, delete-orphan',
            doc="""
            List of claims which this "child" row makes against rows within a
            truck dump batch.
            """))

    claimed_row_uuid = sa.Column(sa.String(length=32), nullable=False)
    claimed_row = orm.relationship(
        PurchaseBatchRow,
        foreign_keys='PurchaseBatchRowClaim.claimed_row_uuid',
        doc="""
        Reference to the truck dump batch row which is claimed by the "child" row.
        """,
        backref=orm.backref(
            'claims',
            cascade='all, delete-orphan',
            doc="""
            List of claims made by "child" rows against this truck dump batch row.
            """))

    cases_received = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Number of cases of product which were ultimately received, and are involved in the claim.
    """)

    units_received = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Number of units of product which were ultimately received, and are involved in the claim.
    """)

    cases_damaged = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Number of cases of product which were shipped damaged, and are involved in the claim.
    """)

    units_damaged = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Number of units of product which were shipped damaged, and are involved in the claim.
    """)

    cases_expired = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Number of cases of product which were shipped expired, and are involved in the claim.
    """)

    units_expired = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Number of units of product which were shipped expired, and are involved in the claim.
    """)

    # TODO: should have fields for mispick here too, right?

    def is_empty(self):
        """
        Returns boolean indicating whether the claim is "empty" - i.e. if it
        has zero or null for all of its quantity fields.
        """
        if self.cases_received:
            return False
        if self.units_received:
            return False

        if self.cases_damaged:
            return False
        if self.units_damaged:
            return False

        if self.cases_expired:
            return False
        if self.units_expired:
            return False

        return True


class PurchaseBatchCredit(PurchaseCreditBase, Base):
    """
    Represents a working copy of purchase credit tied to a batch row.
    """
    __tablename__ = 'purchase_batch_credit'

    @declared_attr
    def __table_args__(cls):
        return cls.__purchasecredit_table_args__() + (
            sa.ForeignKeyConstraint(['row_uuid'], ['purchase_batch_row.uuid'], name='purchase_batch_credit_fk_row'),
        )

    uuid = uuid_column()

    row_uuid = sa.Column(sa.String(length=32), nullable=True)

    row = orm.relationship(
        PurchaseBatchRow,
        doc="""
        Reference to the batch row with which the credit is associated.
        """,
        backref=orm.backref(
            'credits',
            cascade='all, delete-orphan',
            doc="""
            List of :class:`PurchaseBatchCredit` instances for the row.
            """))
