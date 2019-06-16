# -*- coding: utf-8; -*-
"""add product_future_cost

Revision ID: d3b6e3c971b4
Revises: c1bfb033050d
Create Date: 2018-04-09 22:27:06.234782

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = 'd3b6e3c971b4'
down_revision = u'c1bfb033050d'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # product_future_cost
    op.create_table('product_future_cost',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('cost_uuid', sa.String(length=32), nullable=True),
                    sa.Column('product_uuid', sa.String(length=32), nullable=False),
                    sa.Column('vendor_uuid', sa.String(length=32), nullable=False),
                    sa.Column('order_code', sa.String(length=20), nullable=True),
                    sa.Column('case_quantity', sa.Numeric(precision=9, scale=4), nullable=True),
                    sa.Column('case_cost', sa.Numeric(precision=9, scale=5), nullable=True),
                    sa.Column('unit_cost', sa.Numeric(precision=9, scale=5), nullable=True),
                    sa.Column('starts', sa.DateTime(), nullable=False),
                    sa.Column('ends', sa.DateTime(), nullable=True),
                    sa.Column('discontinued', sa.Boolean(), nullable=True),
                    sa.ForeignKeyConstraint(['cost_uuid'], [u'product_cost.uuid'], name=u'product_future_cost_fk_cost'),
                    sa.ForeignKeyConstraint(['product_uuid'], [u'product.uuid'], name=u'product_future_cost_fk_product'),
                    sa.ForeignKeyConstraint(['vendor_uuid'], [u'vendor.uuid'], name=u'product_future_cost_fk_vendor'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # product_future_cost
    op.drop_table('product_future_cost')
