# -*- coding: utf-8 -*-
"""add pricing batch

Revision ID: 3f266c89a3d4
Revises: 20ec527fad0a
Create Date: 2016-11-21 18:01:48.938952

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '3f266c89a3d4'
down_revision = u'20ec527fad0a'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


batch_id_seq = sa.Sequence('batch_id_seq')


def upgrade():

    # batch_pricing
    op.create_table('batch_pricing',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('created', sa.DateTime(), nullable=False),
                    sa.Column('created_by_uuid', sa.String(length=32), nullable=False),
                    sa.Column('cognized', sa.DateTime(), nullable=True),
                    sa.Column('cognized_by_uuid', sa.String(length=32), nullable=True),
                    sa.Column('rowcount', sa.Integer(), nullable=True),
                    sa.Column('executed', sa.DateTime(), nullable=True),
                    sa.Column('executed_by_uuid', sa.String(length=32), nullable=True),
                    sa.Column('purge', sa.Date(), nullable=True),
                    sa.ForeignKeyConstraint(['cognized_by_uuid'], [u'user.uuid'], name=u'batch_pricing_fk_cognized_by'),
                    sa.ForeignKeyConstraint(['created_by_uuid'], [u'user.uuid'], name=u'batch_pricing_fk_created_by'),
                    sa.ForeignKeyConstraint(['executed_by_uuid'], [u'user.uuid'], name=u'batch_pricing_fk_executed_by'),
                    sa.PrimaryKeyConstraint('uuid')
    )

    # batch_pricing_row
    op.create_table('batch_pricing_row',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('batch_uuid', sa.String(length=32), nullable=False),
                    sa.Column('sequence', sa.Integer(), nullable=False),
                    sa.Column('status_code', sa.Integer(), nullable=True),
                    sa.Column('status_text', sa.String(length=255), nullable=True),
                    sa.Column('removed', sa.Boolean(), nullable=False),
                    sa.Column('upc', rattail.db.types.GPCType(), nullable=True),
                    sa.Column('product_uuid', sa.String(length=32), nullable=True),
                    sa.Column('brand_name', sa.String(length=100), nullable=True),
                    sa.Column('description', sa.String(length=255), nullable=True),
                    sa.Column('size', sa.String(length=255), nullable=True),
                    sa.Column('department_number', sa.Integer(), nullable=True),
                    sa.Column('department_name', sa.String(length=30), nullable=True),
                    sa.Column('regular_unit_cost', sa.Numeric(precision=9, scale=5), nullable=True),
                    sa.Column('discounted_unit_cost', sa.Numeric(precision=9, scale=5), nullable=True),
                    sa.Column('old_price', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.Column('price_margin', sa.Numeric(precision=5, scale=3), nullable=True),
                    sa.Column('price_markup', sa.Numeric(precision=4, scale=2), nullable=True),
                    sa.Column('new_price', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.Column('price_diff', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.ForeignKeyConstraint(['batch_uuid'], [u'batch_pricing.uuid'], name=u'batch_pricing_row_fk_batch'),
                    sa.ForeignKeyConstraint(['product_uuid'], [u'product.uuid'], name=u'batch_pricing_row_fk_product'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # batch_pricing_row
    op.drop_table('batch_pricing_row')

    # batch_pricing
    op.drop_table('batch_pricing')
