# -*- coding: utf-8 -*-
"""add price batch thresholds

Revision ID: 45d7d92f4aa6
Revises: 86042c0323c6
Create Date: 2017-01-30 14:59:11.155785

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '45d7d92f4aa6'
down_revision = u'86042c0323c6'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


batch_id_seq = sa.Sequence('batch_id_seq')


def upgrade():

    # batch_pricing
    op.add_column('batch_pricing', sa.Column('min_diff_threshold', sa.Numeric(precision=6, scale=2), nullable=True))


def downgrade():

    # batch_pricing
    op.drop_column('batch_pricing', 'min_diff_threshold')
