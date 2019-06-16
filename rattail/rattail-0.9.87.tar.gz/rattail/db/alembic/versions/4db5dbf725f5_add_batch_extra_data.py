# -*- coding: utf-8; -*-
"""add batch.extra_data

Revision ID: 4db5dbf725f5
Revises: fd7cf00b2918
Create Date: 2019-01-09 11:14:06.009995

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '4db5dbf725f5'
down_revision = 'fd7cf00b2918'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_*
    op.add_column('batch_handheld', sa.Column('extra_data', sa.Text(), nullable=True))
    op.add_column('batch_importer', sa.Column('extra_data', sa.Text(), nullable=True))
    op.add_column('batch_inventory', sa.Column('extra_data', sa.Text(), nullable=True))
    op.add_column('batch_pricing', sa.Column('extra_data', sa.Text(), nullable=True))
    op.add_column('label_batch', sa.Column('extra_data', sa.Text(), nullable=True))
    op.add_column('purchase_batch', sa.Column('extra_data', sa.Text(), nullable=True))
    op.add_column('vendor_catalog', sa.Column('extra_data', sa.Text(), nullable=True))
    op.add_column('vendor_invoice', sa.Column('extra_data', sa.Text(), nullable=True))


def downgrade():

    # batch_*
    op.drop_column('vendor_invoice', 'extra_data')
    op.drop_column('vendor_catalog', 'extra_data')
    op.drop_column('purchase_batch', 'extra_data')
    op.drop_column('label_batch', 'extra_data')
    op.drop_column('batch_pricing', 'extra_data')
    op.drop_column('batch_inventory', 'extra_data')
    op.drop_column('batch_importer', 'extra_data')
    op.drop_column('batch_handheld', 'extra_data')
