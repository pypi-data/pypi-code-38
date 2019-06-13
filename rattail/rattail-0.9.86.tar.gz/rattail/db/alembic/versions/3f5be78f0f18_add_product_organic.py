# -*- coding: utf-8 -*-
"""add product.organic

Revision ID: 3f5be78f0f18
Revises: 3ef0fbcfb42e
Create Date: 2015-02-25 00:12:42.696926

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '3f5be78f0f18'
down_revision = u'3ef0fbcfb42e'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # product.organic
    op.add_column('product', sa.Column('organic', sa.Boolean(), nullable=True))
    product = sa.sql.table('product', sa.sql.column('organic'))
    op.execute(product.update().values({'organic': False}))
    op.alter_column('product', 'organic', nullable=False)
    op.add_column('product_version', sa.Column('organic', sa.Boolean(), nullable=True))


def downgrade():

    # product.organic
    op.drop_column('product_version', 'organic')
    op.drop_column('product', 'organic')
