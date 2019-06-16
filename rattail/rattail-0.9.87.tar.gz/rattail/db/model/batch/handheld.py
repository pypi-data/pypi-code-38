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
Model for handheld batches
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy as sa

from rattail.db.model import Base, FileBatchMixin, ProductBatchRowMixin


class HandheldBatch(FileBatchMixin, Base):
    """
    Batch representing a file from a batch-oriented handheld device
    (e.g. Motorola).
    """
    __tablename__ = 'batch_handheld'
    __batchrow_class__ = 'HandheldBatchRow'
    batch_key = 'handheld'

    # TODO: this should probably be new default
    filename_nullable = True

    device_type = sa.Column(sa.String(length=50), nullable=True, doc="""
    Key indicating the type of device where the batch originated.
    """)

    device_name = sa.Column(sa.String(length=50), nullable=True, doc="""
    Name of the device where the batch originated.
    """)


class HandheldBatchRow(ProductBatchRowMixin, Base):
    """
    Rows for handheld batches.
    """
    __tablename__ = 'batch_handheld_row'
    __batch_class__ = HandheldBatch

    STATUS_OK = 1
    STATUS_PRODUCT_NOT_FOUND = 2

    STATUS = {
        STATUS_OK:                      "ok",
        STATUS_PRODUCT_NOT_FOUND:       "product not found",
    }

    cases = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Case quantity for the record.
    """)

    units = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Unit quantity for the record.
    """)
