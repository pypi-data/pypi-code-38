# -*- coding: utf-8; -*-
"""add item_id for product batches

Revision ID: fd935205655d
Revises: 69d924015613
Create Date: 2017-07-18 23:39:02.717734

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'fd935205655d'
down_revision = u'69d924015613'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch*
    op.add_column('batch_handheld_row', sa.Column('item_id', sa.String(length=20), nullable=True))
    op.add_column('batch_inventory_row', sa.Column('item_id', sa.String(length=20), nullable=True))
    op.add_column('batch_pricing_row', sa.Column('item_id', sa.String(length=20), nullable=True))
    op.add_column('label_batch_row', sa.Column('item_id', sa.String(length=20), nullable=True))
    op.add_column('vendor_invoice_row', sa.Column('item_id', sa.String(length=20), nullable=True))


def downgrade():

    # batch*
    op.drop_column('vendor_invoice_row', 'item_id')
    op.drop_column('label_batch_row', 'item_id')
    op.drop_column('batch_pricing_row', 'item_id')
    op.drop_column('batch_inventory_row', 'item_id')
    op.drop_column('batch_handheld_row', 'item_id')
