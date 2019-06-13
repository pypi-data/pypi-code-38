# -*- coding: utf-8; -*-
"""add vendor_catalog.future

Revision ID: 0174642e7b60
Revises: d3b6e3c971b4
Create Date: 2018-04-09 22:36:01.163993

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '0174642e7b60'
down_revision = u'd3b6e3c971b4'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # vendor_catalog
    op.add_column('vendor_catalog', sa.Column('future', sa.Boolean(), nullable=True))
    op.add_column('vendor_catalog_row', sa.Column('ends', sa.DateTime(), nullable=True))
    op.add_column('vendor_catalog_row', sa.Column('starts', sa.DateTime(), nullable=True))


def downgrade():

    # vendor_catalog
    op.drop_column('vendor_catalog_row', 'starts')
    op.drop_column('vendor_catalog_row', 'ends')
    op.drop_column('vendor_catalog', 'future')
