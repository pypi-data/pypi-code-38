# -*- coding: utf-8; -*-
"""add product_cost.discount

Revision ID: 35b451f8cc27
Revises: adcb91f473c3
Create Date: 2018-11-01 16:45:52.932517

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '35b451f8cc27'
down_revision = 'adcb91f473c3'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # product_cost
    op.add_column('product_cost', sa.Column('discount_amount', sa.Numeric(precision=9, scale=5), nullable=True))
    op.add_column('product_cost', sa.Column('discount_cost', sa.Numeric(precision=9, scale=5), nullable=True))
    op.add_column('product_cost', sa.Column('discount_ends', sa.DateTime(), nullable=True))
    op.add_column('product_cost', sa.Column('discount_percent', sa.Numeric(precision=7, scale=4), nullable=True))
    op.add_column('product_cost', sa.Column('discount_starts', sa.DateTime(), nullable=True))
    op.add_column('product_cost_version', sa.Column('discount_amount', sa.Numeric(precision=9, scale=5), autoincrement=False, nullable=True))
    op.add_column('product_cost_version', sa.Column('discount_cost', sa.Numeric(precision=9, scale=5), autoincrement=False, nullable=True))
    op.add_column('product_cost_version', sa.Column('discount_ends', sa.DateTime(), autoincrement=False, nullable=True))
    op.add_column('product_cost_version', sa.Column('discount_percent', sa.Numeric(precision=7, scale=4), autoincrement=False, nullable=True))
    op.add_column('product_cost_version', sa.Column('discount_starts', sa.DateTime(), autoincrement=False, nullable=True))


def downgrade():

    # product_cost
    op.drop_column('product_cost_version', 'discount_starts')
    op.drop_column('product_cost_version', 'discount_percent')
    op.drop_column('product_cost_version', 'discount_ends')
    op.drop_column('product_cost_version', 'discount_cost')
    op.drop_column('product_cost_version', 'discount_amount')
    op.drop_column('product_cost', 'discount_starts')
    op.drop_column('product_cost', 'discount_percent')
    op.drop_column('product_cost', 'discount_ends')
    op.drop_column('product_cost', 'discount_cost')
    op.drop_column('product_cost', 'discount_amount')
