# -*- coding: utf-8 -*-
"""add purchases

Revision ID: 3350e0220faf
Revises: cd23a59c5d89
Create Date: 2016-11-05 16:12:05.364513

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '3350e0220faf'
down_revision = u'cd23a59c5d89'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


batch_id_seq = sa.Sequence('batch_id_seq')


def upgrade():

    # purchase
    op.create_table('purchase',
                    sa.Column('store_uuid', sa.String(length=32), nullable=False),
                    sa.Column('vendor_uuid', sa.String(length=32), nullable=False),
                    sa.Column('buyer_uuid', sa.String(length=32), nullable=False),
                    sa.Column('po_number', sa.String(length=20), nullable=True),
                    sa.Column('po_total', sa.Numeric(precision=8, scale=2), nullable=True),
                    sa.Column('date_ordered', sa.Date(), nullable=True),
                    sa.Column('date_shipped', sa.Date(), nullable=True),
                    sa.Column('date_received', sa.Date(), nullable=True),
                    sa.Column('invoice_number', sa.String(length=20), nullable=True),
                    sa.Column('invoice_date', sa.Date(), nullable=True),
                    sa.Column('invoice_total', sa.Numeric(precision=8, scale=2), nullable=True),
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('status', sa.Integer(), nullable=False),
                    sa.Column('created', sa.DateTime(), nullable=False),
                    sa.Column('created_by_uuid', sa.String(length=32), nullable=False),
                    sa.ForeignKeyConstraint(['buyer_uuid'], [u'employee.uuid'], name=u'purchase_purchase_fk_buyer'),
                    sa.ForeignKeyConstraint(['created_by_uuid'], [u'user.uuid'], name=u'purchase_fk_created_by'),
                    sa.ForeignKeyConstraint(['store_uuid'], [u'store.uuid'], name=u'purchase_fk_store'),
                    sa.ForeignKeyConstraint(['vendor_uuid'], [u'vendor.uuid'], name=u'purchase_fk_vendor'),
                    sa.PrimaryKeyConstraint('uuid')
    )

    # purchase_item
    op.create_table('purchase_item',
                    sa.Column('sequence', sa.Integer(), nullable=True),
                    sa.Column('vendor_code', sa.String(length=20), nullable=True),
                    sa.Column('product_uuid', sa.String(length=32), nullable=True),
                    sa.Column('upc', rattail.db.types.GPCType(), nullable=True),
                    sa.Column('brand_name', sa.String(length=100), nullable=True),
                    sa.Column('description', sa.String(length=60), nullable=False),
                    sa.Column('size', sa.String(length=255), nullable=True),
                    sa.Column('department_number', sa.Integer(), nullable=True),
                    sa.Column('department_name', sa.String(length=30), nullable=True),
                    sa.Column('case_quantity', sa.Numeric(precision=8, scale=2), nullable=True),
                    sa.Column('cases_ordered', sa.Numeric(precision=10, scale=4), nullable=True),
                    sa.Column('units_ordered', sa.Numeric(precision=10, scale=4), nullable=True),
                    sa.Column('po_unit_cost', sa.Numeric(precision=7, scale=3), nullable=True),
                    sa.Column('po_total', sa.Numeric(precision=7, scale=2), nullable=True),
                    sa.Column('cases_received', sa.Numeric(precision=10, scale=4), nullable=True),
                    sa.Column('units_received', sa.Numeric(precision=10, scale=4), nullable=True),
                    sa.Column('invoice_line_number', sa.Integer(), nullable=True),
                    sa.Column('invoice_case_cost', sa.Numeric(precision=7, scale=3), nullable=True),
                    sa.Column('invoice_unit_cost', sa.Numeric(precision=7, scale=3), nullable=True),
                    sa.Column('invoice_total', sa.Numeric(precision=7, scale=2), nullable=True),
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('purchase_uuid', sa.String(length=32), nullable=False),
                    sa.Column('status', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['product_uuid'], [u'product.uuid'], name=u'purchase_item_fk_product'),
                    sa.ForeignKeyConstraint(['purchase_uuid'], [u'purchase.uuid'], name=u'purchase_item_fk_purchase'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # purchase_item
    op.drop_table('purchase_item')

    # purchase
    op.drop_table('purchase')
