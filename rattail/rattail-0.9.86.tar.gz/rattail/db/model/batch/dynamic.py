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
Dynamic Batches
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy as sa

from rattail.db.model import Base, BatchMixin


class DynamicBatchMixin(BatchMixin):
    """
    Mixin for all dynamic batch (header) classes.
    """

    row_table = sa.Column(sa.String(length=255), nullable=False, doc="""
    Name of the row data table for the batch.  This will typically be a UUID
    and the table will exist within the 'batch' schema in the PostgreSQL DB.
    """)

    # TODO: should nullable be False?
    batch_handler_spec = sa.Column(sa.String(length=255), nullable=True, doc="""
    Object spec for the batch handler.
    """)


class ImporterBatch(DynamicBatchMixin, Base):
    """
    Dynamic batch for use with arbitrary data importers.
    """
    __tablename__ = 'batch_importer'
    batch_key = 'importer'

    import_handler_spec = sa.Column(sa.String(length=255), nullable=False, doc="""
    Object spec for the import handler.
    """)

    host_title = sa.Column(sa.String(length=255), nullable=False, doc="""
    Host title for the import handler.
    """)

    local_title = sa.Column(sa.String(length=255), nullable=False, doc="""
    Local title for the import handler.
    """)

    importer_key = sa.Column(sa.String(length=100), nullable=False, doc="""
    Importer "key" - must be valid within context of the import handler.
    """)
