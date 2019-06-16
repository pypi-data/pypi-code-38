# -*- coding: utf-8; -*-
"""add manual flag to price batch

Revision ID: 6a02ca0279c9
Revises: e63d53698e9f
Create Date: 2017-11-28 16:38:38.683408

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '6a02ca0279c9'
down_revision = u'e63d53698e9f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # batch_pricing*
    op.add_column('batch_pricing', sa.Column('calculate_for_manual', sa.Boolean(), nullable=True))
    op.add_column('batch_pricing_row', sa.Column('manually_priced', sa.Boolean(), nullable=True))


def downgrade():

    # batch_pricing*
    op.drop_column('batch_pricing_row', 'manually_priced')
    op.drop_column('batch_pricing', 'calculate_for_manual')
