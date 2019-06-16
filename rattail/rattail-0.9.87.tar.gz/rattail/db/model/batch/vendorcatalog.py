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
Models for vendor catalog batches
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr

from rattail.db.model import Base, Vendor, FileBatchMixin, ProductBatchRowMixin
from rattail.db.types import GPCType


class VendorCatalog(FileBatchMixin, Base):
    """
    Vendor catalog, the source data file of which has been provided by a user,
    and may be further processed in some site-specific way.
    """
    __tablename__ = 'vendor_catalog'
    __batchrow_class__ = 'VendorCatalogRow'

    @declared_attr
    def __table_args__(cls):
        return cls.__default_table_args__() + (
            sa.ForeignKeyConstraint(['vendor_uuid'], ['vendor.uuid'],
                                    name='vendor_catalog_fk_vendor'),
            )

    parser_key = sa.Column(sa.String(length=100), nullable=False, doc="""
    The key of the parser used to parse the contents of the data file.
    """)

    vendor_uuid = sa.Column(sa.String(length=32), nullable=False)
    vendor = orm.relationship(Vendor, doc="""
    Reference to the :class:`Vendor` to which the catalog pertains.
    """)

    future = sa.Column(sa.Boolean(), nullable=True, default=False, doc="""
    Flag indicating whether the batch should be treated as a "future cost"
    batch, as opposed to a "current" cost batch.  If set, the batch will create
    :class:`ProductFutureCost` records when executed.
    """)

    effective = sa.Column(sa.Date(), nullable=True, doc="""
    General effective date for the catalog, as determined by the data file.  Note
    that not all catalog files will include this; also, some catalogs include
    effective dates on a per-product basis.
    """)


class VendorCatalogRow(ProductBatchRowMixin, Base):
    """
    Row of data within a vendor catalog.
    """
    __tablename__ = 'vendor_catalog_row'
    __batch_class__ = VendorCatalog

    @declared_attr
    def __table_args__(cls):
        return cls.__default_table_args__() + (
            sa.ForeignKeyConstraint(['cost_uuid'], ['product_cost.uuid'],
                                    name='vendor_catalog_row_fk_cost'),
        )

    STATUS_NO_CHANGE = 1
    STATUS_NEW_COST = 2
    STATUS_UPDATE_COST = 3      # TODO: deprecate/remove this one
    STATUS_PRODUCT_NOT_FOUND = 4
    STATUS_CHANGE_VENDOR_ITEM_CODE = 5
    STATUS_CHANGE_CASE_SIZE = 6
    STATUS_CHANGE_COST = 7

    STATUS = {
        STATUS_NO_CHANGE:               "no change",
        STATUS_NEW_COST:                "new cost",
        STATUS_UPDATE_COST:             "cost update", # TODO: deprecate/remove this one
        STATUS_PRODUCT_NOT_FOUND:       "product not found",
        STATUS_CHANGE_VENDOR_ITEM_CODE: "change vendor item code",
        STATUS_CHANGE_CASE_SIZE:        "change case size",
        STATUS_CHANGE_COST:             "change cost",
    }

    cost_uuid = sa.Column(sa.String(length=32), nullable=True)
    cost = orm.relationship(
        'ProductCost', doc="""
        Reference to the :class:`ProductCost` record with which this row is
        associated, if any.
        """,
        backref=orm.backref(
            '_vendor_catalog_rows', doc="""
            List of vendor catalog batch rows which associate directly with
            this cost record.
            """))

    vendor_code = sa.Column(sa.String(length=30), nullable=True, doc="""
    Vendor's unique code for the product.  The meaning of this corresponds to that
    of the :attr:`ProductCost.code` column.
    """)

    case_size = sa.Column(sa.Integer(), nullable=False, default=1, doc="""
    Number of units in a case of product.
    """)

    case_cost = sa.Column(sa.Numeric(precision=10, scale=5), nullable=True, doc="""
    Cost per case of the product.
    """)

    unit_cost = sa.Column(sa.Numeric(precision=10, scale=5), nullable=True, doc="""
    Cost per unit of the product.
    """)

    old_vendor_code = sa.Column(sa.String(length=30), nullable=True, doc="""
    Original vendor code for the product, if any.
    """)

    old_case_size = sa.Column(sa.Integer(), nullable=False, default=1, doc="""
    Original case size for the product, if any.
    """)

    old_case_cost = sa.Column(sa.Numeric(precision=10, scale=5), nullable=True, doc="""
    Original case cost for the product, if any.
    """)

    old_unit_cost = sa.Column(sa.Numeric(precision=10, scale=5), nullable=True, doc="""
    Original unit cost for the product, if any.
    """)

    case_cost_diff = sa.Column(sa.Numeric(precision=10, scale=5), nullable=True, doc="""
    Case cost difference between the catalog and product's original cost record.
    """)

    unit_cost_diff = sa.Column(sa.Numeric(precision=10, scale=5), nullable=True, doc="""
    Unit cost difference between the catalog and product's original cost record.
    """)

    suggested_retail = sa.Column(sa.Numeric(precision=7, scale=2), nullable=True, doc="""
    Suggested retail price for the item, according to this vendor.
    """)

    starts = sa.Column(sa.DateTime(), nullable=True, doc="""
    Date and time when the cost becomes effective, if applicable/known.  This
    should probably be set for a future batch of course, but otherwise
    shouldn't matter.
    """)

    ends = sa.Column(sa.DateTime(), nullable=True, doc="""
    Date and time when the cost *stops* being effective, if applicable/known.
    This often will be null, in which case the cost becomes "permanently"
    effective, i.e. until a newer cost is brought in.
    """)

    discount_starts = sa.Column(sa.DateTime(), nullable=True, doc="""
    Date and time when the "allowance" (temporary discount) for the cost
    begins, if applicable.
    """)

    discount_ends = sa.Column(sa.DateTime(), nullable=True, doc="""
    Date and time when the "allowance" (temporary discount) for the cost ends,
    if applicable.
    """)

    discount_amount = sa.Column(sa.Numeric(precision=9, scale=5), nullable=True, doc="""
    Dollar amount of the "allowance" (temporary discount) for the cost, if
    applicable.
    """)

    discount_percent = sa.Column(sa.Numeric(precision=7, scale=4), nullable=True, doc="""
    Percentage amount of the "allowance" (temporary discount) for the cost, if
    applicable.
    """)
