# -*- coding: utf-8 -*-
"""add batchrow.status_text

Revision ID: 2dd756a44a16
Revises: 218562884128
Create Date: 2015-02-14 04:02:22.262221

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '2dd756a44a16'
down_revision = u'218562884128'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():
    op.add_column('vendor_catalog_row', sa.Column('status_text', sa.String(length=255), nullable=True))
    op.add_column('vendor_invoice_row', sa.Column('status_text', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('vendor_invoice_row', 'status_text')
    op.drop_column('vendor_catalog_row', 'status_text')
