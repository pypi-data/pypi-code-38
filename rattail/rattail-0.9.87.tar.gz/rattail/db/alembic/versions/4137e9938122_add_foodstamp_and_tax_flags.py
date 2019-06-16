# -*- coding: utf-8 -*-
"""add foodstamp and tax flags

Revision ID: 4137e9938122
Revises: 6c68c814f3c2
Create Date: 2016-08-08 20:08:14.467886

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '4137e9938122'
down_revision = u'6c68c814f3c2'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # product
    op.add_column('product', sa.Column('food_stampable', sa.Boolean(), nullable=True))
    op.add_column('product', sa.Column('tax1', sa.Boolean(), nullable=True))
    op.add_column('product', sa.Column('tax2', sa.Boolean(), nullable=True))
    op.add_column('product', sa.Column('tax3', sa.Boolean(), nullable=True))


def downgrade():

    # product
    op.drop_column('product', 'tax3')
    op.drop_column('product', 'tax2')
    op.drop_column('product', 'tax1')
    op.drop_column('product', 'food_stampable')
