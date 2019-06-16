# -*- coding: utf-8 -*-
"""add product.discountable

Revision ID: 3c33f288ad62
Revises: 3544687ae150
Create Date: 2015-02-27 00:28:50.454692

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '3c33f288ad62'
down_revision = u'3544687ae150'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # product.discountable
    op.add_column('product', sa.Column('discountable', sa.Boolean(), nullable=True))
    product = sa.sql.table('product', sa.sql.column('discountable'))
    op.execute(product.update().values({'discountable': True}))
    op.alter_column('product', 'discountable', nullable=False)
    op.add_column('product_version', sa.Column('discountable', sa.Boolean(), nullable=True))


def downgrade():

    # product.discountable
    op.drop_column('product_version', 'discountable')
    op.drop_column('product', 'discountable')
