# -*- coding: utf-8 -*-
"""add batch status

Revision ID: 043d4bafc0be
Revises: 4d2c5bdfecff
Create Date: 2017-06-21 12:44:38.709412

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '043d4bafc0be'
down_revision = u'4d2c5bdfecff'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # batch.status_code, batch.status_text
    op.add_column('batch_handheld', sa.Column('status_code', sa.Integer(), nullable=True))
    op.add_column('batch_handheld', sa.Column('status_text', sa.String(length=255), nullable=True))
    op.add_column('batch_inventory', sa.Column('status_code', sa.Integer(), nullable=True))
    op.add_column('batch_inventory', sa.Column('status_text', sa.String(length=255), nullable=True))
    op.add_column('batch_pricing', sa.Column('status_code', sa.Integer(), nullable=True))
    op.add_column('batch_pricing', sa.Column('status_text', sa.String(length=255), nullable=True))
    op.add_column('label_batch', sa.Column('status_code', sa.Integer(), nullable=True))
    op.add_column('label_batch', sa.Column('status_text', sa.String(length=255), nullable=True))
    op.add_column('purchase_batch', sa.Column('status_code', sa.Integer(), nullable=True))
    op.add_column('purchase_batch', sa.Column('status_text', sa.String(length=255), nullable=True))
    op.add_column('vendor_catalog', sa.Column('status_code', sa.Integer(), nullable=True))
    op.add_column('vendor_catalog', sa.Column('status_text', sa.String(length=255), nullable=True))
    op.add_column('vendor_invoice', sa.Column('status_code', sa.Integer(), nullable=True))
    op.add_column('vendor_invoice', sa.Column('status_text', sa.String(length=255), nullable=True))


def downgrade():

    # batch.status_code, batch.status_text
    op.drop_column('vendor_invoice', 'status_text')
    op.drop_column('vendor_invoice', 'status_code')
    op.drop_column('vendor_catalog', 'status_text')
    op.drop_column('vendor_catalog', 'status_code')
    op.drop_column('purchase_batch', 'status_text')
    op.drop_column('purchase_batch', 'status_code')
    op.drop_column('label_batch', 'status_text')
    op.drop_column('label_batch', 'status_code')
    op.drop_column('batch_pricing', 'status_text')
    op.drop_column('batch_pricing', 'status_code')
    op.drop_column('batch_inventory', 'status_text')
    op.drop_column('batch_inventory', 'status_code')
    op.drop_column('batch_handheld', 'status_text')
    op.drop_column('batch_handheld', 'status_code')
