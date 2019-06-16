# -*- coding: utf-8 -*-
"""add catalog.suggested_retail

Revision ID: 3f1e4a7b5268
Revises: fb4bd12cbd37
Create Date: 2017-12-05 12:56:02.603397

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '3f1e4a7b5268'
down_revision = u'fb4bd12cbd37'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # vendor_catalog_row
    op.add_column('vendor_catalog_row', sa.Column('suggested_retail', sa.Numeric(precision=7, scale=2), nullable=True))


def downgrade():

    # vendor_catalog_row
    op.drop_column('vendor_catalog_row', 'suggested_retail')
