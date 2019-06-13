# -*- coding: utf-8; -*-
"""add item codes for pricing batch

Revision ID: 5dee2f796f25
Revises: 727c63fcde2d
Create Date: 2019-04-18 18:11:32.100480

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '5dee2f796f25'
down_revision = '727c63fcde2d'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_pricing_row
    op.add_column('batch_pricing_row', sa.Column('alternate_code', sa.String(length=20), nullable=True))
    op.add_column('batch_pricing_row', sa.Column('family_code', sa.Integer(), nullable=True))
    op.add_column('batch_pricing_row', sa.Column('report_code', sa.Integer(), nullable=True))
    op.add_column('batch_pricing_row', sa.Column('vendor_item_code', sa.String(length=20), nullable=True))


def downgrade():

    # batch_pricing_row
    op.drop_column('batch_pricing_row', 'vendor_item_code')
    op.drop_column('batch_pricing_row', 'report_code')
    op.drop_column('batch_pricing_row', 'family_code')
    op.drop_column('batch_pricing_row', 'alternate_code')
