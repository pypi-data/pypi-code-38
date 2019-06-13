# -*- coding: utf-8 -*-
"""add batch_row.modified

Revision ID: 830a20917c49
Revises: d67dee1cb849
Create Date: 2018-07-10 08:58:35.083616

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '830a20917c49'
down_revision = u'd67dee1cb849'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_row
    op.add_column('batch_handheld_row', sa.Column('modified', sa.DateTime(), nullable=True))
    op.add_column('batch_inventory_row', sa.Column('modified', sa.DateTime(), nullable=True))
    op.add_column('batch_pricing_row', sa.Column('modified', sa.DateTime(), nullable=True))
    op.add_column('label_batch_row', sa.Column('modified', sa.DateTime(), nullable=True))
    op.add_column('purchase_batch_row', sa.Column('modified', sa.DateTime(), nullable=True))
    op.add_column('vendor_catalog_row', sa.Column('modified', sa.DateTime(), nullable=True))
    op.add_column('vendor_invoice_row', sa.Column('modified', sa.DateTime(), nullable=True))


def downgrade():

    # batch_row
    op.drop_column('vendor_invoice_row', 'modified')
    op.drop_column('vendor_catalog_row', 'modified')
    op.drop_column('purchase_batch_row', 'modified')
    op.drop_column('label_batch_row', 'modified')
    op.drop_column('batch_pricing_row', 'modified')
    op.drop_column('batch_inventory_row', 'modified')
    op.drop_column('batch_handheld_row', 'modified')
