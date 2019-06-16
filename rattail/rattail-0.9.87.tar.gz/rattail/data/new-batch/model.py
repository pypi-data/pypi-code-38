# -*- coding: utf-8; -*-
# -*- coding: utf-8; -*-
"""
Data model for ${model_title} batches
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr

from rattail.db import model


class ${model_name}(model.FileBatchMixin, model.Base):
    """
    Primary data model for ${model_title} batches.
    """
    __tablename__ = '${table_name}'
    __batchrow_class__ = '${model_name}Row'

    # NOTE: The columns / constraints / relationships shown here are meant to
    # be examples only; please edit as you like.

    @declared_attr
    def __table_args__(cls):
        return cls.__default_table_args__() + (
            sa.ForeignKeyConstraint(['vendor_uuid'], ['vendor.uuid'],
                                    name='${table_name}_fk_vendor'),
        )

    vendor_uuid = sa.Column(sa.String(length=32), nullable=False)

    vendor = orm.relationship(
        Vendor, doc="""
        Reference to the :class:`Vendor` to which the batch pertains.
        """,
        backref=orm.backref('_${table_name}', cascade='all'))

    effective = sa.Column(sa.Date(), nullable=True, doc="""
    Date on which the batch should be considered effective.
    """)


class ${model_name}Row(model.ProductBatchRowMixin, model.Base):
    """
    Row of data within a ${model_title} batch.
    """
    __tablename__ = '${table_name}_row'
    __batch_class__ = ${model_name}

    # NOTE: The columns / constraints / relationships shown here are meant to
    # be examples only; please edit as you like.

    @declared_attr
    def __table_args__(cls):
        return cls.__default_table_args__() + (
            sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'],
                                    name='${table_name}_row_fk_product'),
        )

    STATUS_OK = 1
    STATUS_SOME_CONCERN = 2
    STATUS_UTTER_CHAOS = 3

    STATUS = {
        STATUS_OK:              "groovy",
        STATUS_SOME_CONCERN:    "should look into this one",
        STATUS_UTTER_CHAOS:     "the world just ended",
    }

    upc = sa.Column(model.GPCType(), nullable=True, doc="""
    UPC for the row.
    """)

    product_uuid = sa.Column(sa.String(length=32), nullable=True)

    product = orm.relationship(
        Product,
        doc="""
        Reference to the :class:`Product` with which the row is associated, if any.
        """,
        backref=orm.backref('_${table_name}_rows', cascade='all'))

    description = sa.Column(sa.String(length=255), nullable=False, default='', doc="""
    Description of the product.
    """)

    unit_cost = sa.Column(sa.Numeric(precision=9, scale=5), nullable=True, doc="""
    Cost per unit of the product.
    """)
