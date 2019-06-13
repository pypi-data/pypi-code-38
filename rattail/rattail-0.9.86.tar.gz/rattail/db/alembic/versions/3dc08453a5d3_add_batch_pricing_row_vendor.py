# -*- coding: utf-8 -*-
"""add batch_pricing_row.vendor

Revision ID: 3dc08453a5d3
Revises: 45d7d92f4aa6
Create Date: 2017-02-02 15:26:15.851844

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '3dc08453a5d3'
down_revision = u'45d7d92f4aa6'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # batch_pricing_row
    op.add_column('batch_pricing_row', sa.Column('vendor_uuid', sa.String(length=32), nullable=True))
    op.create_foreign_key(u'batch_pricing_row_fk_vendor', 'batch_pricing_row', 'vendor', ['vendor_uuid'], ['uuid'])


def downgrade():

    # batch_pricing_row
    op.drop_constraint(u'batch_pricing_row_fk_vendor', 'batch_pricing_row', type_='foreignkey')
    op.drop_column('batch_pricing_row', 'vendor_uuid')
