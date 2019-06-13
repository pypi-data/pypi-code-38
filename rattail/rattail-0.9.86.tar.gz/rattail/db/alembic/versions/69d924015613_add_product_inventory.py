# -*- coding: utf-8; -*-
"""add product inventory

Revision ID: 69d924015613
Revises: a28c3583c8f0
Create Date: 2017-07-18 21:27:41.750784

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '69d924015613'
down_revision = u'a28c3583c8f0'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # product_inventory
    op.create_table('product_inventory',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('product_uuid', sa.String(length=32), nullable=False),
                    sa.Column('on_hand', sa.Numeric(precision=9, scale=4), nullable=True),
                    sa.Column('on_order', sa.Numeric(precision=9, scale=4), nullable=True),
                    sa.ForeignKeyConstraint(['product_uuid'], [u'product.uuid'], name=u'product_inventory_fk_product'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # product_inventory
    op.drop_table('product_inventory')
