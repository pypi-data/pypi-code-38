# -*- coding: utf-8; -*-
"""add columns for vendor catalog

Revision ID: ccd32c44393f
Revises: 90a3338b187b
Create Date: 2018-04-05 20:14:40.596713

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = 'ccd32c44393f'
down_revision = u'90a3338b187b'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # vendor_catalog_row
    op.add_column('vendor_catalog_row', sa.Column('department_name', sa.String(length=30), nullable=True))
    op.add_column('vendor_catalog_row', sa.Column('department_number', sa.Integer(), nullable=True))
    op.add_column('vendor_catalog_row', sa.Column('item_id', sa.String(length=20), nullable=True))
    op.alter_column('vendor_catalog_row', 'description', nullable=True)


def downgrade():

    # vendor_catalog_row
    op.alter_column('vendor_catalog_row', 'description', nullable=False)
    op.drop_column('vendor_catalog_row', 'item_id')
    op.drop_column('vendor_catalog_row', 'department_number')
    op.drop_column('vendor_catalog_row', 'department_name')
