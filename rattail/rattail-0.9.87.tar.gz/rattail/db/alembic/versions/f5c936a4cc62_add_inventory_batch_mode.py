# -*- coding: utf-8 -*-
"""add inventory batch mode

Revision ID: f5c936a4cc62
Revises: 1f8e3cf6b2a2
Create Date: 2016-08-22 21:41:25.359322

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = 'f5c936a4cc62'
down_revision = u'1f8e3cf6b2a2'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


batch_id_seq = sa.Sequence('batch_id_seq')


def upgrade():

    # batch_inventory
    op.add_column('batch_inventory', sa.Column('mode', sa.Integer(), nullable=True))


def downgrade():

    # batch_inventory
    op.drop_column('batch_inventory', 'mode')
