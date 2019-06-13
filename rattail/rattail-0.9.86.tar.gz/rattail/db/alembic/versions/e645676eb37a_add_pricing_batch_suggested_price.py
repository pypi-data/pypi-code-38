# -*- coding: utf-8; -*-
"""add pricing_batch.suggested_price

Revision ID: e645676eb37a
Revises: 5ef33e961026
Create Date: 2018-11-18 19:54:55.006187

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'e645676eb37a'
down_revision = '5ef33e961026'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_pricing_row
    op.add_column('batch_pricing_row', sa.Column('suggested_price', sa.Numeric(precision=8, scale=3), nullable=True))


def downgrade():

    # batch_pricing_row
    op.drop_column('batch_pricing_row', 'suggested_price')
