# -*- coding: utf-8 -*-
"""add batch.notes

Revision ID: 9305c1f493b4
Revises: 528c049eb5b7
Create Date: 2017-02-21 14:07:52.838097

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '9305c1f493b4'
down_revision = u'528c049eb5b7'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # add 'notes' for batch headers
    op.add_column('batch_handheld', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('batch_inventory', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('batch_pricing', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('label_batch', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('purchase_batch', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('vendor_catalog', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('vendor_invoice', sa.Column('notes', sa.Text(), nullable=True))


def downgrade():

    # drop 'notes' for batch headers
    op.drop_column('vendor_invoice', 'notes')
    op.drop_column('vendor_catalog', 'notes')
    op.drop_column('purchase_batch', 'notes')
    op.drop_column('label_batch', 'notes')
    op.drop_column('batch_pricing', 'notes')
    op.drop_column('batch_inventory', 'notes')
    op.drop_column('batch_handheld', 'notes')
