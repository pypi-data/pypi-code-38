# -*- coding: utf-8; -*-
"""add pricing_batch.margin_diff

Revision ID: d28d28bc3cd0
Revises: e645676eb37a
Create Date: 2018-11-18 21:02:37.435757

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'd28d28bc3cd0'
down_revision = 'e645676eb37a'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_pricing_row
    op.add_column('batch_pricing_row', sa.Column('margin_diff', sa.Numeric(precision=6, scale=3), nullable=True))
    op.add_column('batch_pricing_row', sa.Column('price_diff_percent', sa.Numeric(precision=8, scale=3), nullable=True))


def downgrade():

    # batch_pricing_row
    op.drop_column('batch_pricing_row', 'price_diff_percent')
    op.drop_column('batch_pricing_row', 'margin_diff')
