# -*- coding: utf-8 -*-
"""add purchase credits

Revision ID: 193c2dcdd14d
Revises: 123af5f6a0bc
Create Date: 2016-12-09 17:03:39.001046

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '193c2dcdd14d'
down_revision = u'123af5f6a0bc'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


batch_id_seq = sa.Sequence('batch_id_seq')


def upgrade():

    # purchase_batch_row
    op.add_column('purchase_batch_row', sa.Column('cases_mispick', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('purchase_batch_row', sa.Column('units_mispick', sa.Numeric(precision=10, scale=4), nullable=True))

    # purchase_item
    op.add_column('purchase_item', sa.Column('cases_mispick', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('purchase_item', sa.Column('units_mispick', sa.Numeric(precision=10, scale=4), nullable=True))

    # purchase_credit
    op.create_table('purchase_credit',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('store_uuid', sa.String(length=32), nullable=False),
                    sa.Column('vendor_uuid', sa.String(length=32), nullable=False),
                    sa.Column('date_ordered', sa.Date(), nullable=True),
                    sa.Column('date_shipped', sa.Date(), nullable=True),
                    sa.Column('date_received', sa.Date(), nullable=True),
                    sa.Column('invoice_number', sa.String(length=20), nullable=True),
                    sa.Column('invoice_date', sa.Date(), nullable=True),
                    sa.Column('credit_type', sa.String(length=20), nullable=False),
                    sa.Column('product_uuid', sa.String(length=32), nullable=True),
                    sa.Column('upc', rattail.db.types.GPCType(), nullable=True),
                    sa.Column('brand_name', sa.String(length=100), nullable=True),
                    sa.Column('description', sa.String(length=60), nullable=False),
                    sa.Column('size', sa.String(length=255), nullable=True),
                    sa.Column('department_number', sa.Integer(), nullable=True),
                    sa.Column('department_name', sa.String(length=30), nullable=True),
                    sa.Column('case_quantity', sa.Numeric(precision=8, scale=2), nullable=True),
                    sa.Column('cases_shorted', sa.Numeric(precision=10, scale=4), nullable=True),
                    sa.Column('units_shorted', sa.Numeric(precision=10, scale=4), nullable=True),
                    sa.Column('expiration_date', sa.Date(), nullable=True),
                    sa.Column('invoice_line_number', sa.Integer(), nullable=True),
                    sa.Column('invoice_case_cost', sa.Numeric(precision=7, scale=3), nullable=True),
                    sa.Column('invoice_unit_cost', sa.Numeric(precision=7, scale=3), nullable=True),
                    sa.Column('invoice_total', sa.Numeric(precision=7, scale=2), nullable=True),
                    sa.Column('purchase_uuid', sa.String(length=32), nullable=True),
                    sa.Column('item_uuid', sa.String(length=32), nullable=True),
                    sa.Column('status', sa.Integer(), nullable=True),
                    sa.Column('mispick_brand_name', sa.String(length=100), nullable=True),
                    sa.Column('mispick_description', sa.String(length=60), nullable=True),
                    sa.Column('mispick_product_uuid', sa.String(length=32), nullable=True),
                    sa.Column('mispick_size', sa.String(length=255), nullable=True),
                    sa.Column('mispick_upc', rattail.db.types.GPCType(), nullable=True),
                    sa.ForeignKeyConstraint(['item_uuid'], [u'purchase_item.uuid'], name=u'purchase_credit_fk_item'),
                    sa.ForeignKeyConstraint(['product_uuid'], [u'product.uuid'], name=u'purchase_credit_fk_product'),
                    sa.ForeignKeyConstraint(['purchase_uuid'], [u'purchase.uuid'], name=u'purchase_credit_fk_purchase'),
                    sa.ForeignKeyConstraint(['store_uuid'], [u'store.uuid'], name=u'purchase_credit_fk_store'),
                    sa.ForeignKeyConstraint(['vendor_uuid'], [u'vendor.uuid'], name=u'purchase_credit_fk_vendor'),
                    sa.ForeignKeyConstraint(['mispick_product_uuid'], [u'product.uuid'], name=u'purchase_credit_fk_mispick_product'),
                    sa.PrimaryKeyConstraint('uuid')
    )

    # purchase_batch_credit
    op.create_table('purchase_batch_credit',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('row_uuid', sa.String(length=32), nullable=True),
                    sa.Column('store_uuid', sa.String(length=32), nullable=False),
                    sa.Column('vendor_uuid', sa.String(length=32), nullable=False),
                    sa.Column('date_ordered', sa.Date(), nullable=True),
                    sa.Column('date_shipped', sa.Date(), nullable=True),
                    sa.Column('date_received', sa.Date(), nullable=True),
                    sa.Column('invoice_number', sa.String(length=20), nullable=True),
                    sa.Column('invoice_date', sa.Date(), nullable=True),
                    sa.Column('credit_type', sa.String(length=20), nullable=False),
                    sa.Column('product_uuid', sa.String(length=32), nullable=True),
                    sa.Column('upc', rattail.db.types.GPCType(), nullable=True),
                    sa.Column('brand_name', sa.String(length=100), nullable=True),
                    sa.Column('description', sa.String(length=60), nullable=False),
                    sa.Column('size', sa.String(length=255), nullable=True),
                    sa.Column('department_number', sa.Integer(), nullable=True),
                    sa.Column('department_name', sa.String(length=30), nullable=True),
                    sa.Column('case_quantity', sa.Numeric(precision=8, scale=2), nullable=True),
                    sa.Column('cases_shorted', sa.Numeric(precision=10, scale=4), nullable=True),
                    sa.Column('units_shorted', sa.Numeric(precision=10, scale=4), nullable=True),
                    sa.Column('expiration_date', sa.Date(), nullable=True),
                    sa.Column('invoice_line_number', sa.Integer(), nullable=True),
                    sa.Column('invoice_case_cost', sa.Numeric(precision=7, scale=3), nullable=True),
                    sa.Column('invoice_unit_cost', sa.Numeric(precision=7, scale=3), nullable=True),
                    sa.Column('invoice_total', sa.Numeric(precision=7, scale=2), nullable=True),
                    sa.Column('mispick_brand_name', sa.String(length=100), nullable=True),
                    sa.Column('mispick_description', sa.String(length=60), nullable=True),
                    sa.Column('mispick_product_uuid', sa.String(length=32), nullable=True),
                    sa.Column('mispick_size', sa.String(length=255), nullable=True),
                    sa.Column('mispick_upc', rattail.db.types.GPCType(), nullable=True),
                    sa.ForeignKeyConstraint(['product_uuid'], [u'product.uuid'], name=u'purchase_batch_credit_fk_product'),
                    sa.ForeignKeyConstraint(['row_uuid'], [u'purchase_batch_row.uuid'], name=u'purchase_batch_credit_fk_row'),
                    sa.ForeignKeyConstraint(['store_uuid'], [u'store.uuid'], name=u'purchase_batch_credit_fk_store'),
                    sa.ForeignKeyConstraint(['vendor_uuid'], [u'vendor.uuid'], name=u'purchase_batch_credit_fk_vendor'),
                    sa.ForeignKeyConstraint(['mispick_product_uuid'], [u'product.uuid'], name=u'purchase_batch_credit_fk_mispick_product'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # purchase_batch_credit
    op.drop_table('purchase_batch_credit')

    # purchase_credit
    op.drop_table('purchase_credit')

    # purchase_item
    op.drop_column('purchase_item', 'units_mispick')
    op.drop_column('purchase_item', 'cases_mispick')

    # purchase_batch_row
    op.drop_column('purchase_batch_row', 'units_mispick')
    op.drop_column('purchase_batch_row', 'cases_mispick')
