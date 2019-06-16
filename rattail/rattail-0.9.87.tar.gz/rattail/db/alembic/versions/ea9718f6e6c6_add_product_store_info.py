# -*- coding: utf-8 -*-
"""add product_store_info

Revision ID: ea9718f6e6c6
Revises: 86632a7bc5b5
Create Date: 2017-05-24 12:39:41.665427

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'ea9718f6e6c6'
down_revision = u'86632a7bc5b5'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # product_store_info
    op.create_table('product_store_info',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('product_uuid', sa.String(length=32), nullable=False),
                    sa.Column('store_uuid', sa.String(length=32), nullable=False),
                    sa.Column('recently_active', sa.Boolean(), nullable=True),
                    sa.ForeignKeyConstraint(['product_uuid'], [u'product.uuid'], name=u'product_store_info_fk_product'),
                    sa.ForeignKeyConstraint(['store_uuid'], [u'store.uuid'], name=u'product_store_info_fk_store'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # product_store_info
    op.drop_table('product_store_info')
