# -*- coding: utf-8 -*-
"""add purchase batch

Revision ID: 9a5511fdc9f5
Revises: 3350e0220faf
Create Date: 2016-11-05 16:33:00.953452

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '9a5511fdc9f5'
down_revision = u'3350e0220faf'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


batch_id_seq = sa.Sequence('batch_id_seq')


def upgrade():

    # purchase_batch
    op.create_table('purchase_batch',
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
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('created', sa.DateTime(), nullable=False),
                    sa.Column('created_by_uuid', sa.String(length=32), nullable=False),
                    sa.Column('cognized', sa.DateTime(), nullable=True),
                    sa.Column('cognized_by_uuid', sa.String(length=32), nullable=True),
                    sa.Column('rowcount', sa.Integer(), nullable=True),
                    sa.Column('executed', sa.DateTime(), nullable=True),
                    sa.Column('executed_by_uuid', sa.String(length=32), nullable=True),
                    sa.Column('purge', sa.Date(), nullable=True),
                    sa.ForeignKeyConstraint(['buyer_uuid'], [u'employee.uuid'], name=u'purchase_batch_purchase_fk_buyer'),
                    sa.ForeignKeyConstraint(['cognized_by_uuid'], [u'user.uuid'], name=u'purchase_batch_fk_cognized_by'),
                    sa.ForeignKeyConstraint(['created_by_uuid'], [u'user.uuid'], name=u'purchase_batch_fk_created_by'),
                    sa.ForeignKeyConstraint(['executed_by_uuid'], [u'user.uuid'], name=u'purchase_batch_fk_executed_by'),
                    sa.ForeignKeyConstraint(['store_uuid'], [u'store.uuid'], name=u'purchase_batch_fk_store'),
                    sa.ForeignKeyConstraint(['vendor_uuid'], [u'vendor.uuid'], name=u'purchase_batch_fk_vendor'),
                    sa.PrimaryKeyConstraint('uuid')
    )

    # purchase_batch_row
    op.create_table('purchase_batch_row',
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
                    sa.Column('batch_uuid', sa.String(length=32), nullable=False),
                    sa.Column('sequence', sa.Integer(), nullable=False),
                    sa.Column('status_code', sa.Integer(), nullable=True),
                    sa.Column('status_text', sa.String(length=255), nullable=True),
                    sa.Column('removed', sa.Boolean(), nullable=False),
                    sa.ForeignKeyConstraint(['batch_uuid'], [u'purchase_batch.uuid'], name=u'purchase_batch_row_fk_batch_uuid'),
                    sa.ForeignKeyConstraint(['product_uuid'], [u'product.uuid'], name=u'purchase_batch_row_fk_product'),
                    sa.PrimaryKeyConstraint('uuid')
    )
    

def downgrade():

    # purchase_batch_row
    op.drop_table('purchase_batch_row')

    # purchase_batch
    op.drop_table('purchase_batch')
