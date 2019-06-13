# -*- coding: utf-8; -*-
"""add allowances to vendorcatalog batch

Revision ID: 727c63fcde2d
Revises: 4e5526fae79e
Create Date: 2019-04-18 16:16:44.844542

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '727c63fcde2d'
down_revision = '4e5526fae79e'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # vendor_catalog_row
    op.add_column('vendor_catalog_row', sa.Column('discount_amount', sa.Numeric(precision=9, scale=5), nullable=True))
    op.add_column('vendor_catalog_row', sa.Column('discount_ends', sa.DateTime(), nullable=True))
    op.add_column('vendor_catalog_row', sa.Column('discount_percent', sa.Numeric(precision=7, scale=4), nullable=True))
    op.add_column('vendor_catalog_row', sa.Column('discount_starts', sa.DateTime(), nullable=True))


def downgrade():

    # vendor_catalog_row
    op.drop_column('vendor_catalog_row', 'discount_starts')
    op.drop_column('vendor_catalog_row', 'discount_percent')
    op.drop_column('vendor_catalog_row', 'discount_ends')
    op.drop_column('vendor_catalog_row', 'discount_amount')
