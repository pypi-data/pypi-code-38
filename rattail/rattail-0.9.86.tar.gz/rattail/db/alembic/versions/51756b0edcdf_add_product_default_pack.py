# -*- coding: utf-8; -*-
"""add product.default_pack

Revision ID: 51756b0edcdf
Revises: a295dee8d1e9
Create Date: 2018-07-03 19:56:26.827825

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '51756b0edcdf'
down_revision = u'a295dee8d1e9'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # product
    op.add_column('product', sa.Column('default_pack', sa.Boolean(), nullable=True))
    op.add_column('product_version', sa.Column('default_pack', sa.Boolean(), autoincrement=False, nullable=True))


def downgrade():

    # product
    op.drop_column('product_version', 'default_pack')
    op.drop_column('product', 'default_pack')
