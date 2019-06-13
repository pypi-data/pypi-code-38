# -*- coding: utf-8 -*-
"""add product.last_sold

Revision ID: 3623367c499f
Revises: 6cadbeb3f82
Create Date: 2015-03-10 16:02:27.105206

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '3623367c499f'
down_revision = u'6cadbeb3f82'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # product.last_sold
    op.add_column('product', sa.Column('last_sold', sa.DateTime(), nullable=True))
    op.add_column('product_version', sa.Column('last_sold', sa.DateTime(), nullable=True))


def downgrade():

    # product.last_sold
    op.drop_column('product_version', 'last_sold')
    op.drop_column('product', 'last_sold')
