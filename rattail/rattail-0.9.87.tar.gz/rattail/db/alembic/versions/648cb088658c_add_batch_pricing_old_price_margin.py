# -*- coding: utf-8; -*-
"""add batch_pricing.old_price_margin

Revision ID: 648cb088658c
Revises: 04f17c46b42f
Create Date: 2018-11-30 19:20:03.161013

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '648cb088658c'
down_revision = '04f17c46b42f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_pricing_row
    op.add_column('batch_pricing_row', sa.Column('old_price_margin', sa.Numeric(precision=8, scale=3), nullable=True))


def downgrade():

    # batch_pricing_row
    op.drop_column('batch_pricing_row', 'old_price_margin')
