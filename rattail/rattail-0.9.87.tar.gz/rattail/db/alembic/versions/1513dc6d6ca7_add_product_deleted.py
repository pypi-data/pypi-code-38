# -*- coding: utf-8 -*-
"""add product.deleted

Revision ID: 1513dc6d6ca7
Revises: 47d30c955111
Create Date: 2015-02-10 22:17:45.367561

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '1513dc6d6ca7'
down_revision = u'47d30c955111'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # add product.deleted
    op.add_column('product', sa.Column('deleted', sa.Boolean(), nullable=True))
    product = sa.sql.table('product', sa.sql.column('deleted'))
    op.execute(product.update().values({'deleted': False}))
    op.alter_column('product', 'deleted', nullable=False)
    op.add_column('product_version', sa.Column('deleted', sa.Boolean(), nullable=True))


def downgrade():

    # drop product.deleted
    op.drop_column('product_version', 'deleted')
    op.drop_column('product', 'deleted')
