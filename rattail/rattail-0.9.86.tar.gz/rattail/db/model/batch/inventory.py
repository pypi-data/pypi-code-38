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
Model for inventory batches
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.orderinglist import ordering_list

from rattail.db.model import Base, BatchMixin, ProductBatchRowMixin, uuid_column, getset_factory


class InventoryBatch(BatchMixin, Base):
    """
    Batch for product inventory counts; note that this requires a data file.
    """
    __tablename__ = 'batch_inventory'
    __batchrow_class__ = 'InventoryBatchRow'
    batch_key = 'inventory'

    @declared_attr
    def __table_args__(cls):
        return cls.__default_table_args__() + (
            sa.ForeignKeyConstraint(['handheld_batch_uuid'], ['batch_handheld.uuid'],
                                    name='batch_inventory_fk_handheld_batch'),
            )

    handheld_batch_uuid = sa.Column(sa.String(length=32), nullable=True)

    handheld_batch = orm.relationship(
        'HandheldBatch',
        doc="""
        Reference to the handheld batch from which this inventory batch originated.
        """,
        backref=orm.backref('inventory_batch', uselist=False, doc="""
        Reference to the inventory batch to which this handheld batch was converted.
        """))

    mode = sa.Column(sa.Integer(), nullable=True, doc="""
    Specifies the "mode" for the inventory count batch, i.e. how the count data
    should ultimately be interpreted/applied.
    """)

    reason_code = sa.Column(sa.String(length=50), nullable=True, doc="""
    Specifies the "reason code" for an inventory adjustment batch, i.e.  what
    happened / why the adjustment is required.  Interpretation of this value is
    the responsibility of custom logic.
    """)

    total_cost = sa.Column(sa.Numeric(precision=12, scale=5), nullable=True, doc="""
    Total inventory cost for the batch, if known.
    """)


class InventoryBatchFromHandheld(Base):
    """
    Primary data model for inventory batches.
    """
    __tablename__ = 'batch_inventory_handheld'
    __table_args__ = (
        sa.ForeignKeyConstraint(['batch_uuid'], ['batch_inventory.uuid'],
                                name='batch_inventory_handheld_fk_batch'),
        sa.ForeignKeyConstraint(['handheld_uuid'], ['batch_handheld.uuid'],
                                name='batch_inventory_handheld_fk_handheld'),
    )

    uuid = uuid_column()

    batch_uuid = sa.Column(sa.String(length=32), nullable=False)
    ordinal = sa.Column(sa.Integer(), nullable=False)
    batch = orm.relationship(
        InventoryBatch,
        doc="""
        Reference to the inventory batch, with which handheld batch(es) are associated.
        """,
        backref=orm.backref(
            '_handhelds',
            collection_class=ordering_list('ordinal', count_from=1),
            order_by=ordinal,
            cascade='all, delete-orphan',
            doc="""
            Sequence of raw inventory / handheld batch associations.
            """))
    
    handheld_uuid = sa.Column(sa.String(length=32), nullable=False)
    handheld = orm.relationship(
        'HandheldBatch',
        doc="""
        Reference to the handheld batch from which this inventory batch originated.
        """,
        backref=orm.backref(
            '_inventory_batch',
            uselist=False,
            cascade='all, delete-orphan',
            doc="""
            Indirect reference to the inventory batch to which this handheld batch was converted.
            """))


InventoryBatch.handheld_batches = association_proxy('_handhelds', 'handheld',
                                                    creator=lambda batch: InventoryBatchFromHandheld(handheld=batch),
                                                    getset_factory=getset_factory)


class InventoryBatchRow(ProductBatchRowMixin, Base):
    """
    Rows for inventory batches.
    """
    __tablename__ = 'batch_inventory_row'
    __batch_class__ = InventoryBatch

    STATUS_OK = 1
    STATUS_PRODUCT_NOT_FOUND = 2

    STATUS = {
        STATUS_OK:                      "ok",
        STATUS_PRODUCT_NOT_FOUND:       "product not found",
    }

    previous_units_on_hand = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Previous on-hand unit quantity for the item, i.e. before the count.
    """)

    cases = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Case quantity for the record.
    """)

    units = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Unit quantity for the record.
    """)

    case_quantity = sa.Column(sa.Numeric(precision=6, scale=2), nullable=True, doc="""
    Number of units in a case of product.
    """)

    variance = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    This is essentially the difference between the "supposed" number of units
    on-hand at the time of count, and the actual number of units counted.  May
    be useful for reporting, or for a "delayed" adjustment to actual inventory
    levels.
    """)

    unit_cost = sa.Column(sa.Numeric(precision=9, scale=5), nullable=True, doc="""
    Inventory unit cost for the item, if known.
    """)

    total_cost = sa.Column(sa.Numeric(precision=12, scale=5), nullable=True, doc="""
    Total inventory cost for the item (i.e. taking quantity into account), if known.
    """)

    @property
    def full_unit_quantity(self):
        if self.cases is not None or self.units is not None:
            return self.units or 0 + (self.cases or 0) * (self.case_quantity or 1)

    @property
    def case_cost(self):
        if self.case_quantity and self.unit_cost:
            return self.case_quantity * self.unit_cost
