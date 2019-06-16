# -*- coding: utf-8 -*-
"""add dept to product batch

Revision ID: cd23a59c5d89
Revises: 14d83595afa1
Create Date: 2016-10-15 19:49:14.208311

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = 'cd23a59c5d89'
down_revision = u'14d83595afa1'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


batch_id_seq = sa.Sequence('batch_id_seq')


def upgrade():

    # "product batch rows"
    op.add_column('batch_handheld_row', sa.Column('department_name', sa.String(length=30), nullable=True))
    op.add_column('batch_handheld_row', sa.Column('department_number', sa.Integer(), nullable=True))
    op.add_column('batch_inventory_row', sa.Column('department_name', sa.String(length=30), nullable=True))
    op.add_column('batch_inventory_row', sa.Column('department_number', sa.Integer(), nullable=True))
    op.add_column('vendor_invoice_row', sa.Column('department_name', sa.String(length=30), nullable=True))
    op.add_column('vendor_invoice_row', sa.Column('department_number', sa.Integer(), nullable=True))


def downgrade():

    # "product batch rows"
    op.drop_column('vendor_invoice_row', 'department_number')
    op.drop_column('vendor_invoice_row', 'department_name')
    op.drop_column('batch_inventory_row', 'department_number')
    op.drop_column('batch_inventory_row', 'department_name')
    op.drop_column('batch_handheld_row', 'department_number')
    op.drop_column('batch_handheld_row', 'department_name')
