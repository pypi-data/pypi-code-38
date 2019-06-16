# -*- coding: utf-8 -*-
"""add vendor_invoice

Revision ID: 218562884128
Revises: 268ff6454410
Create Date: 2015-02-13 21:51:41.779081

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '218562884128'
down_revision = u'268ff6454410'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():
    op.create_table('vendor_invoice',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('created', sa.DateTime(), nullable=False),
                    sa.Column('created_by_uuid', sa.String(length=32), nullable=False),
                    sa.Column('cognized', sa.DateTime(), nullable=True),
                    sa.Column('cognized_by_uuid', sa.String(length=32), nullable=True),
                    sa.Column('rowcount', sa.Integer(), nullable=True),
                    sa.Column('executed', sa.DateTime(), nullable=True),
                    sa.Column('executed_by_uuid', sa.String(length=32), nullable=True),
                    sa.Column('purge', sa.Date(), nullable=True),
                    sa.Column('filename', sa.String(length=255), nullable=False),
                    sa.Column('parser_key', sa.String(length=100), nullable=False),
                    sa.Column('vendor_uuid', sa.String(length=32), nullable=False),
                    sa.Column('invoice_date', sa.Date(), nullable=True),
                    sa.Column('purchase_order_number', sa.String(length=20), nullable=True),
                    sa.ForeignKeyConstraint(['cognized_by_uuid'], [u'user.uuid'], name=u'vendor_invoice_fk_cognized_by'),
                    sa.ForeignKeyConstraint(['created_by_uuid'], [u'user.uuid'], name=u'vendor_invoice_fk_created_by'),
                    sa.ForeignKeyConstraint(['executed_by_uuid'], [u'user.uuid'], name=u'vendor_invoice_fk_executed_by'),
                    sa.ForeignKeyConstraint(['vendor_uuid'], [u'vendor.uuid'], name=u'vendor_invoice_fk_vendor'),
                    sa.PrimaryKeyConstraint('uuid')
                    )
    op.create_table('vendor_invoice_row',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('batch_uuid', sa.String(length=32), nullable=False),
                    sa.Column('sequence', sa.Integer(), nullable=False),
                    sa.Column('status_code', sa.Integer(), nullable=True),
                    sa.Column('removed', sa.Boolean(), nullable=False),
                    sa.Column('upc', rattail.db.types.GPCType(), nullable=True),
                    sa.Column('product_uuid', sa.String(length=32), nullable=True),
                    sa.Column('brand_name', sa.String(length=100), nullable=True),
                    sa.Column('description', sa.String(length=255), nullable=True),
                    sa.Column('size', sa.String(length=255), nullable=True),
                    sa.Column('vendor_code', sa.String(length=30), nullable=True),
                    sa.Column('case_quantity', sa.Integer(), nullable=False),
                    sa.Column('ordered_cases', sa.Integer(), nullable=True),
                    sa.Column('ordered_units', sa.Integer(), nullable=True),
                    sa.Column('shipped_cases', sa.Integer(), nullable=True),
                    sa.Column('shipped_units', sa.Integer(), nullable=True),
                    sa.Column('case_cost', sa.Numeric(precision=9, scale=5), nullable=True),
                    sa.Column('unit_cost', sa.Numeric(precision=9, scale=5), nullable=True),
                    sa.Column('total_cost', sa.Numeric(precision=9, scale=5), nullable=True),
                    sa.Column('line_number', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['batch_uuid'], [u'vendor_invoice.uuid'], name=u'vendor_invoice_row_fk_batch'),
                    sa.ForeignKeyConstraint(['product_uuid'], [u'product.uuid'], name=u'vendor_invoice_row_fk_product'),
                    sa.PrimaryKeyConstraint('uuid')
                    )


def downgrade():
    op.drop_table('vendor_invoice_row')
    op.drop_table('vendor_invoice')
