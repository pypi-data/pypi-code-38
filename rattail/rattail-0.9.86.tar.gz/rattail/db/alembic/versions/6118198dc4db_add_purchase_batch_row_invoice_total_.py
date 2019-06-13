# -*- coding: utf-8; -*-
"""add purchase_batch_row.invoice_total_calculated

Revision ID: 6118198dc4db
Revises: 03be1584f923
Create Date: 2019-03-07 13:45:36.687862

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '6118198dc4db'
down_revision = '03be1584f923'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # purchase_batch
    op.add_column('purchase_batch', sa.Column('invoice_total_calculated', sa.Numeric(precision=8, scale=2), nullable=True))

    # purchase_batch_row
    op.add_column('purchase_batch_row', sa.Column('invoice_total_calculated', sa.Numeric(precision=7, scale=2), nullable=True))


def downgrade():

    # purchase_batch_row
    op.drop_column('purchase_batch_row', 'invoice_total_calculated')

    # purchase_batch
    op.drop_column('purchase_batch', 'invoice_total_calculated')
