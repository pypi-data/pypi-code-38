# -*- coding: utf-8 -*-
"""add some product flags

Revision ID: 7ba105af22a7
Revises: 9305c1f493b4
Create Date: 2017-02-22 19:05:30.964165

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '7ba105af22a7'
down_revision = u'9305c1f493b4'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # product
    op.add_column('product', sa.Column('gluten_free', sa.Boolean(), nullable=True))
    op.add_column('product', sa.Column('kosher', sa.Boolean(), nullable=True))
    op.add_column('product', sa.Column('sugar_free', sa.Boolean(), nullable=True))
    op.add_column('product', sa.Column('vegan', sa.Boolean(), nullable=True))
    op.add_column('product', sa.Column('vegetarian', sa.Boolean(), nullable=True))


def downgrade():

    # product
    op.drop_column('product', 'vegetarian')
    op.drop_column('product', 'vegan')
    op.drop_column('product', 'sugar_free')
    op.drop_column('product', 'kosher')
    op.drop_column('product', 'gluten_free')
