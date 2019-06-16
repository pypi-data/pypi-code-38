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
Data model for label batches
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.orderinglist import ordering_list

from rattail.db.model import Base, LabelProfile, BatchMixin, ProductBatchRowMixin, getset_factory
from rattail.db.core import uuid_column, filename_column


class LabelBatch(BatchMixin, Base):
    """
    Primary data model for label batches.
    """
    __tablename__ = 'label_batch'
    __batchrow_class__ = 'LabelBatchRow'
    batch_key = 'labels'
    model_title = "Label Batch"

    @declared_attr
    def __table_args__(cls):
        return cls.__default_table_args__() + (
            sa.ForeignKeyConstraint(['handheld_batch_uuid'], ['batch_handheld.uuid'],
                                    name='label_batch_fk_handheld_batch'),
            sa.ForeignKeyConstraint(['label_profile_uuid'], ['label_profile.uuid'],
                                    name='label_batch_fk_label_profile'),
        )

    handheld_batch_uuid = sa.Column(sa.String(length=32), nullable=True)

    handheld_batch = orm.relationship(
        'HandheldBatch',
        doc="""
        Reference to the handheld batch from which this label batch originated.
        """,
        backref=orm.backref(
            'label_batch',
            uselist=False,
            doc="""
            Reference to the label batch to which this handheld batch was converted.
            """))

    filename = filename_column()

    static_prices = sa.Column(sa.Boolean(), nullable=True, default=False, doc="""
    Flag indicating whether product prices within the batch should be
    considered "static" or if they should be updated during batch refresh,
    i.e. read from current product record.
    """)

    label_code = sa.Column(sa.String(length=30), nullable=True, doc="""
    Code (string) of the label type (profile) which should be used when
    printing the rows.  Note that each row may override this.
    """)

    label_profile_uuid = sa.Column(sa.String(length=32), nullable=True)
    label_profile = orm.relationship(
        LabelProfile,
        doc="""
        Reference to the label "profile" which contains details of how the
        rows should be printed.  Note that each row may override this.
        """)


class LabelBatchFromHandheld(Base):
    """
    Primary data model for label batches.
    """
    __tablename__ = 'label_batch_handheld'
    __table_args__ = (
        sa.ForeignKeyConstraint(['batch_uuid'], ['label_batch.uuid'],
                                name='label_batch_handheld_fk_batch'),
        sa.ForeignKeyConstraint(['handheld_uuid'], ['batch_handheld.uuid'],
                                name='label_batch_handheld_fk_handheld'),
    )

    uuid = uuid_column()

    batch_uuid = sa.Column(sa.String(length=32), nullable=False)
    ordinal = sa.Column(sa.Integer(), nullable=False)
    batch = orm.relationship(
        LabelBatch,
        doc="""
        Reference to the label batch, with which handheld batch(es) are associated.
        """,
        backref=orm.backref(
            '_handhelds',
            collection_class=ordering_list('ordinal', count_from=1),
            order_by=ordinal,
            cascade='all, delete-orphan',
            doc="""
            Sequence of raw label / handheld batch associations.
            """))
    
    handheld_uuid = sa.Column(sa.String(length=32), nullable=False)
    handheld = orm.relationship(
        'HandheldBatch',
        doc="""
        Reference to the handheld batch from which this label batch originated.
        """,
        backref=orm.backref(
            '_label_batch',
            uselist=False,
            cascade='all, delete-orphan',
            doc="""
            Indirect reference to the label batch to which this handheld batch was converted.
            """))


LabelBatch.handheld_batches = association_proxy('_handhelds', 'handheld',
                                                creator=lambda batch: LabelBatchFromHandheld(handheld=batch),
                                                getset_factory=getset_factory)


class LabelBatchRow(ProductBatchRowMixin, Base):
    """
    Row of data within a label batch.
    """
    __tablename__ = 'label_batch_row'
    __batch_class__ = LabelBatch

    @declared_attr
    def __table_args__(cls):
        return cls.__default_table_args__() + (
            sa.ForeignKeyConstraint(['label_profile_uuid'], ['label_profile.uuid'],
                                    name='label_batch_row_fk_label_profile'),
        )

    STATUS_OK                           = 1
    STATUS_PRODUCT_NOT_FOUND            = 2
    STATUS_LABEL_PROFILE_NOT_FOUND      = 3
    STATUS_REGULAR_PRICE_UNKNOWN        = 4
    STATUS_PRODUCT_APPEARS_INACTIVE     = 5

    STATUS = {
        STATUS_OK                       : "ok",
        STATUS_PRODUCT_NOT_FOUND        : "product not found",
        STATUS_LABEL_PROFILE_NOT_FOUND  : "label profile not found",
        STATUS_REGULAR_PRICE_UNKNOWN    : "regular price unknown",
        STATUS_PRODUCT_APPEARS_INACTIVE : "product appears inactive",
    }

    ####################
    # label fields
    ####################

    label_code = sa.Column(sa.String(length=30), nullable=True, doc="""
    Code (string) of the label type (profile) which should be used when
    printing this row/product.
    """)

    label_profile_uuid = sa.Column(sa.String(length=32), nullable=True)

    label_profile = orm.relationship(
        LabelProfile,
        doc="""
        Reference to the :class:`LabelProfile` with which the row is associated.
        """,
        backref=orm.backref('_print_labels_rows', cascade='all'))

    label_quantity = sa.Column(sa.Integer(), nullable=False, default=1, doc="""
    Number of labels to print for this row/product.
    """)

    ####################
    # product fields
    ####################

    location = sa.Column(sa.String(length=30), nullable=True)
    category_code = sa.Column(sa.String(length=30), nullable=True)
    category_name = sa.Column(sa.String(length=50), nullable=True)
    description_2 = sa.Column(sa.String(length=100), nullable=True)
    regular_price = sa.Column(sa.Numeric(precision=6, scale=2), nullable=True)
    pack_quantity = sa.Column(sa.Integer(), nullable=True)
    pack_price = sa.Column(sa.Numeric(precision=6, scale=2), nullable=True)
    sale_price = sa.Column(sa.Numeric(precision=6, scale=2), nullable=True)
    sale_start = sa.Column(sa.DateTime(), nullable=True)
    sale_stop = sa.Column(sa.DateTime(), nullable=True)
    multi_unit_sale_price = sa.Column(sa.String(length=20), nullable=True)
    comp_unit_size = sa.Column(sa.Numeric(precision=6, scale=2), nullable=True)
    comp_unit_measure = sa.Column(sa.String(length=30), nullable=True)
    comp_unit_reg_price = sa.Column(sa.String(length=10), nullable=True)
    comp_unit_sale_price = sa.Column(sa.String(length=10), nullable=True)
    vendor_id = sa.Column(sa.String(length=10), nullable=True)
    vendor_name = sa.Column(sa.String(length=50), nullable=True)
    vendor_item_code = sa.Column(sa.String(length=15), nullable=True)
    case_quantity = sa.Column(sa.Numeric(precision=6, scale=2), nullable=True)
    tax_code = sa.Column(sa.Integer(), nullable=True)
    crv = sa.Column(sa.Boolean(), nullable=True)
    organic = sa.Column(sa.Boolean(), nullable=True)
    country_of_origin = sa.Column(sa.String(length=100), nullable=True)
