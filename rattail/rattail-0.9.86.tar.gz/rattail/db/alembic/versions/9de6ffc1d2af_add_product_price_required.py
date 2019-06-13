# -*- coding: utf-8 -*-
"""add product.price_required

Revision ID: 9de6ffc1d2af
Revises: 3f1e4a7b5268
Create Date: 2017-12-20 18:07:03.817694

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '9de6ffc1d2af'
down_revision = u'3f1e4a7b5268'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # product
    op.add_column('product', sa.Column('price_required', sa.Boolean(), nullable=True))
    op.add_column('product_version', sa.Column('price_required', sa.Boolean(), autoincrement=False, nullable=True))


def downgrade():

    # product
    op.drop_column('product_version', 'price_required')
    op.drop_column('product', 'price_required')
