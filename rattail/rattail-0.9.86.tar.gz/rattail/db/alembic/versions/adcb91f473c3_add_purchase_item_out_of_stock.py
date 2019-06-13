# -*- coding: utf-8 -*-
"""add purchase_item.out_of_stock

Revision ID: adcb91f473c3
Revises: 0a3dca1cd299
Create Date: 2018-09-25 18:53:21.503034

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'adcb91f473c3'
down_revision = u'0a3dca1cd299'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # purchase_batch_row
    op.add_column('purchase_batch_row', sa.Column('out_of_stock', sa.Boolean(), nullable=True))

    # purchase_item
    op.add_column('purchase_item', sa.Column('out_of_stock', sa.Boolean(), nullable=True))

    # vendor_invoice_row
    op.add_column('vendor_invoice_row', sa.Column('out_of_stock', sa.Boolean(), nullable=True))


def downgrade():

    # vendor_invoice_row
    op.drop_column('vendor_invoice_row', 'out_of_stock')

    # purchase_item
    op.drop_column('purchase_item', 'out_of_stock')

    # purchase_batch_row
    op.drop_column('purchase_batch_row', 'out_of_stock')
