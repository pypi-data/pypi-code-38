# -*- coding: utf-8 -*-
"""add customer.active_in_pos

Revision ID: b9658d212053
Revises: 195ceb6abeb3
Create Date: 2017-05-12 14:38:44.460118

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = 'b9658d212053'
down_revision = u'195ceb6abeb3'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # customer
    op.add_column('customer', sa.Column('active_in_pos', sa.Boolean(), nullable=True))


def downgrade():

    # customer
    op.drop_column('customer', 'active_in_pos')
