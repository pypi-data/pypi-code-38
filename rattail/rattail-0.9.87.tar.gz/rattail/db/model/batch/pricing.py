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
Data model for pricing batches
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr

from rattail.db.model import Base, BatchMixin, ProductBatchRowMixin, Vendor
from rattail.db.core import filename_column


class PricingBatch(BatchMixin, Base):
    """
    Primary data model for pricing batches.
    """
    __tablename__ = 'batch_pricing'
    __batchrow_class__ = 'PricingBatchRow'
    batch_key = 'pricing'
    model_title = "Pricing Batch"

    min_diff_threshold = sa.Column(sa.Numeric(precision=6, scale=2), nullable=True, doc="""
    Threshold amount in currency units (i.e. dollars), to which the new *price
    change* is compared, to determine whether the price change is "minor".
    """)

    min_diff_percent = sa.Column(sa.Numeric(precision=5, scale=2), nullable=True, doc="""
    Percentage to which the new price *margin change* is to be compared, to
    determine whether the price change is "minor".
    """)

    calculate_for_manual = sa.Column(sa.Boolean(), nullable=True, default=False, doc="""
    Flag indicating whether prices should be calculated for products which are
    manually priced under normal circumstances.
    """)

    input_filename = filename_column(nullable=True, doc="""
    Base name of the input data file, if applicable.
    """)


class PricingBatchRow(ProductBatchRowMixin, Base):
    """
    Row of data within a pricing batch.
    """
    __tablename__ = 'batch_pricing_row'
    __batch_class__ = PricingBatch

    @declared_attr
    def __table_args__(cls):
        return cls.__default_table_args__() + (
            sa.ForeignKeyConstraint(['vendor_uuid'], ['vendor.uuid'],
                                    name='batch_pricing_row_fk_vendor'),
        )

    STATUS_PRICE_UNCHANGED              = 1
    STATUS_PRICE_INCREASE               = 2
    STATUS_PRICE_DECREASE               = 3
    STATUS_PRODUCT_NOT_FOUND            = 4
    STATUS_PRODUCT_MANUALLY_PRICED      = 5
    STATUS_CANNOT_CALCULATE_PRICE       = 6
    STATUS_PRICE_INCREASE_MINOR         = 7
    STATUS_PRICE_DECREASE_MINOR         = 8

    STATUS = {
        STATUS_PRICE_UNCHANGED          : "price not changed",
        STATUS_PRICE_INCREASE           : "price increase",
        STATUS_PRICE_INCREASE_MINOR     : "price increase (minor)",
        STATUS_PRICE_DECREASE           : "price drop",
        STATUS_PRICE_DECREASE_MINOR     : "price drop (minor)",
        STATUS_PRODUCT_NOT_FOUND        : "product not found",
        STATUS_PRODUCT_MANUALLY_PRICED  : "product is priced manually",
        STATUS_CANNOT_CALCULATE_PRICE   : "cannot calculate price",
    }

    vendor_uuid = sa.Column(sa.String(length=32), nullable=True)
    vendor = orm.relationship(Vendor)

    vendor_item_code = sa.Column(sa.String(length=20), nullable=True, doc="""
    Vendor-specific code (SKU) for the item.
    """)

    family_code = sa.Column(sa.Integer(), nullable=True, doc="""
    Family code for the item.
    """)

    report_code = sa.Column(sa.Integer(), nullable=True, doc="""
    Report code for the item.
    """)

    alternate_code = sa.Column(sa.String(length=20), nullable=True, doc="""
    Alternate code (UPC, PLU etc.) for the item.
    """)

    regular_unit_cost = sa.Column(sa.Numeric(precision=9, scale=5), nullable=True, doc="""
    The "normal" base unit cost for the item, i.e. with no discounts applied.
    """)

    true_unit_cost = sa.Column(sa.Numeric(precision=9, scale=5), nullable=True, doc="""
    The "true" base unit cost for the item.  Note that this may vary over time
    based on allowances etc.
    """)

    true_margin = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    Profit margin for the "new" price vs. the "true" unit cost
    (:attr:`true_unit_cost`).
    """)

    discounted_unit_cost = sa.Column(sa.Numeric(precision=9, scale=5), nullable=True, doc="""
    The "discounted" base unit cost for the item.  This is meant to be the
    "effective" unit cost which is used as the basis for the price calculation.
    """)

    suggested_price = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    The "suggested" retail price for the item.  This is assumed to be defined
    by some external source, i.e. traditional MSRP as opposed to the price
    being actually suggested by the batch logic.
    """)

    old_price = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    The "old" price for the item.  This is assumed to be the "current" price as
    of batch creation.
    """)

    old_price_margin = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    Profit margin for the "old" price vs. the "effective" unit cost
    (:attr:`discounted_unit_cost`).
    """)

    price_markup = sa.Column(sa.Numeric(precision=5, scale=3), nullable=True, doc="""
    Markup used to calculate new price, if applicable.
    """)

    new_price = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    The "new" price for the item, as calculated by the batch handler logic.
    """)

    price_margin = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    Profit margin for the "new" price vs. the "effective" unit cost
    (:attr:`discounted_unit_cost`).
    """)

    price_diff = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    Difference in dollars, between the new and old price amounts.
    """)

    price_diff_percent = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    Difference in percentage, between the new and old price amounts.
    """)

    margin_diff = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    Difference in margin, between the new and old price margins.
    """)

    manually_priced = sa.Column(sa.Boolean(), nullable=True, doc="""
    Optional flag to indicate whether the product is manually priced, under
    normal circumstances.
    """)
