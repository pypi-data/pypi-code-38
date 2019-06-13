# -*- coding: utf-8; -*-
"""add pricing_batch.min_diff_percent

Revision ID: 7eb0903932ff
Revises: d28d28bc3cd0
Create Date: 2018-11-25 19:47:21.873271

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '7eb0903932ff'
down_revision = 'd28d28bc3cd0'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_pricing
    op.add_column('batch_pricing', sa.Column('min_diff_percent', sa.Numeric(precision=5, scale=2), nullable=True))


def downgrade():

    # batch_pricing
    op.drop_column('batch_pricing', 'min_diff_percent')
