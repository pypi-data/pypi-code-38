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
Data model for generic "product" batches
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr

from rattail.db.model import (Base, BatchMixin, ProductBatchRowMixin,
                              Vendor, Department, Subdepartment)
from rattail.db.core import filename_column


class ProductBatch(BatchMixin, Base):
    """
    Primary data model for product batches.
    """
    __tablename__ = 'batch_product'
    __batchrow_class__ = 'ProductBatchRow'
    batch_key = 'product'
    model_title = "Product Batch"
    model_title_plural = "Product Batches"

    input_filename = filename_column(nullable=True, doc="""
    Base name of the input data file, if applicable.
    """)


class ProductBatchRow(ProductBatchRowMixin, Base):
    """
    Row of data within a product batch.
    """
    __tablename__ = 'batch_product_row'
    __batch_class__ = ProductBatch

    @declared_attr
    def __table_args__(cls):
        return cls.__default_table_args__() + (
            sa.ForeignKeyConstraint(['department_uuid'], ['department.uuid'],
                                    name='batch_product_row_fk_department'),
            sa.ForeignKeyConstraint(['subdepartment_uuid'], ['subdepartment.uuid'],
                                    name='batch_product_row_fk_subdepartment'),
            sa.ForeignKeyConstraint(['category_uuid'], ['category.uuid'],
                                    name='batch_product_row_fk_category'),
            sa.ForeignKeyConstraint(['family_uuid'], ['family.uuid'],
                                    name='batch_product_row_fk_family'),
            sa.ForeignKeyConstraint(['reportcode_uuid'], ['report_code.uuid'],
                                    name='batch_product_row_fk_reportcode'),
            sa.ForeignKeyConstraint(['vendor_uuid'], ['vendor.uuid'],
                                    name='batch_product_row_fk_vendor'),
        )

    STATUS_OK                           = 1
    STATUS_MISSING_KEY                  = 2
    STATUS_PRODUCT_NOT_FOUND            = 3

    STATUS = {
        STATUS_OK                       : "ok",
        STATUS_MISSING_KEY              : "missing product key",
        STATUS_PRODUCT_NOT_FOUND        : "product not found",
    }

    department_uuid = sa.Column(sa.String(length=32), nullable=True)
    department = orm.relationship(Department, doc="""
    Reference to the department to which the product belongs.
    """)

    subdepartment_uuid = sa.Column(sa.String(length=32), nullable=True)
    subdepartment = orm.relationship(Subdepartment, doc="""
    Reference to the subdepartment to which the product belongs.
    """)

    vendor_uuid = sa.Column(sa.String(length=32), nullable=True)
    vendor = orm.relationship(Vendor, doc="""
    Reference to the "preferred" vendor from which product may be purchased.
    """)

    vendor_item_code = sa.Column(sa.String(length=20), nullable=True, doc="""
    Vendor-specific item code (SKU) for the product.
    """)

    category_uuid = sa.Column(sa.String(length=32), nullable=True)
    category = orm.relationship('Category', doc="""
    Reference to the category for the item.
    """)

    family_uuid = sa.Column(sa.String(length=32), nullable=True)
    family = orm.relationship('Family', doc="""
    Reference to the family for the item.
    """)

    reportcode_uuid = sa.Column(sa.String(length=32), nullable=True)
    reportcode = orm.relationship('ReportCode', doc="""
    Reference to the "report code" object for the item.
    """)

    regular_cost = sa.Column(sa.Numeric(precision=9, scale=5), nullable=True, doc="""
    The "base" unit cost for the item, i.e. with no discounts applied.
    """)

    current_cost = sa.Column(sa.Numeric(precision=9, scale=5), nullable=True, doc="""
    The "true" unit cost for the item, i.e. with discounts applied.
    """)

    current_cost_starts = sa.Column(sa.DateTime(), nullable=True, doc="""
    Date/time when the current cost starts, if applicable.
    """)

    current_cost_ends = sa.Column(sa.DateTime(), nullable=True, doc="""
    Date/time when the current cost ends, if applicable.
    """)

    regular_price = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    The "regular" unit price for the item.
    """)

    current_price = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    The "current" unit price for the item.
    """)

    current_price_starts = sa.Column(sa.DateTime(), nullable=True, doc="""
    Date/time when the current price starts, if applicable.
    """)

    current_price_ends = sa.Column(sa.DateTime(), nullable=True, doc="""
    Date/time when the current price ends, if applicable.
    """)

    suggested_price = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    The "suggested" retail price for the item.
    """)
