# -*- coding: utf-8 -*-
"""add product_batch_row.item_entry

Revision ID: 0a3dca1cd299
Revises: 42edf57f1ae2
Create Date: 2018-09-22 19:56:36.431827

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '0a3dca1cd299'
down_revision = u'42edf57f1ae2'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # misc. batches
    op.add_column('batch_handheld_row', sa.Column('item_entry', sa.String(length=20), nullable=True))
    op.add_column('batch_inventory_row', sa.Column('item_entry', sa.String(length=20), nullable=True))
    op.add_column('batch_pricing_row', sa.Column('item_entry', sa.String(length=20), nullable=True))
    op.add_column('label_batch_row', sa.Column('item_entry', sa.String(length=20), nullable=True))
    op.add_column('purchase_batch_row', sa.Column('item_entry', sa.String(length=20), nullable=True))
    op.add_column('vendor_catalog_row', sa.Column('item_entry', sa.String(length=20), nullable=True))
    op.add_column('vendor_invoice_row', sa.Column('item_entry', sa.String(length=20), nullable=True))


def downgrade():

    # misc. batches
    op.drop_column('vendor_invoice_row', 'item_entry')
    op.drop_column('vendor_catalog_row', 'item_entry')
    op.drop_column('purchase_batch_row', 'item_entry')
    op.drop_column('label_batch_row', 'item_entry')
    op.drop_column('batch_pricing_row', 'item_entry')
    op.drop_column('batch_inventory_row', 'item_entry')
    op.drop_column('batch_handheld_row', 'item_entry')
