# -*- coding: utf-8; -*-
"""add product_batch.subdepartment

Revision ID: bd7acb7028da
Revises: c02430f167c2
Create Date: 2018-12-18 16:42:42.152911

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'bd7acb7028da'
down_revision = 'c02430f167c2'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # product-related batches...
    op.add_column('batch_handheld_row', sa.Column('subdepartment_name', sa.String(length=30), nullable=True))
    op.add_column('batch_handheld_row', sa.Column('subdepartment_number', sa.Integer(), nullable=True))
    op.add_column('batch_inventory_row', sa.Column('subdepartment_name', sa.String(length=30), nullable=True))
    op.add_column('batch_inventory_row', sa.Column('subdepartment_number', sa.Integer(), nullable=True))
    op.add_column('batch_pricing_row', sa.Column('subdepartment_name', sa.String(length=30), nullable=True))
    op.add_column('batch_pricing_row', sa.Column('subdepartment_number', sa.Integer(), nullable=True))
    op.add_column('label_batch_row', sa.Column('subdepartment_name', sa.String(length=30), nullable=True))
    op.add_column('label_batch_row', sa.Column('subdepartment_number', sa.Integer(), nullable=True))
    op.add_column('vendor_catalog_row', sa.Column('subdepartment_name', sa.String(length=30), nullable=True))
    op.add_column('vendor_catalog_row', sa.Column('subdepartment_number', sa.Integer(), nullable=True))
    op.add_column('vendor_invoice_row', sa.Column('subdepartment_name', sa.String(length=30), nullable=True))
    op.add_column('vendor_invoice_row', sa.Column('subdepartment_number', sa.Integer(), nullable=True))


def downgrade():

    # product-related batches...
    op.drop_column('vendor_invoice_row', 'subdepartment_number')
    op.drop_column('vendor_invoice_row', 'subdepartment_name')
    op.drop_column('vendor_catalog_row', 'subdepartment_number')
    op.drop_column('vendor_catalog_row', 'subdepartment_name')
    op.drop_column('label_batch_row', 'subdepartment_number')
    op.drop_column('label_batch_row', 'subdepartment_name')
    op.drop_column('batch_pricing_row', 'subdepartment_number')
    op.drop_column('batch_pricing_row', 'subdepartment_name')
    op.drop_column('batch_inventory_row', 'subdepartment_number')
    op.drop_column('batch_inventory_row', 'subdepartment_name')
    op.drop_column('batch_handheld_row', 'subdepartment_number')
    op.drop_column('batch_handheld_row', 'subdepartment_name')
