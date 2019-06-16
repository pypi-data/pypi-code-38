# -*- coding: utf-8 -*-
"""add product.special_order

Revision ID: 321f8f7b3887
Revises: 3f0d2a97f12a
Create Date: 2015-02-27 01:43:24.499865

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '321f8f7b3887'
down_revision = u'3f0d2a97f12a'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # product.special_order
    op.add_column('product', sa.Column('special_order', sa.Boolean(), nullable=True))
    product = sa.sql.table('product', sa.sql.column('special_order'))
    op.execute(product.update().values({'special_order': False}))
    op.alter_column('product', 'special_order', nullable=False)
    op.add_column('product_version', sa.Column('special_order', sa.Boolean(), nullable=True))


def downgrade():

    # product.special_order
    op.drop_column('product_version', 'special_order')
    op.drop_column('product', 'special_order')
