# -*- coding: utf-8; -*-
"""add purchase_batch.po_total_calculated

Revision ID: 64d163d9de3a
Revises: abd43933c6c6
Create Date: 2019-06-07 16:44:15.007878

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '64d163d9de3a'
down_revision = 'abd43933c6c6'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # purchase_batch*
    op.add_column('purchase_batch', sa.Column('po_total_calculated', sa.Numeric(precision=8, scale=2), nullable=True))
    op.add_column('purchase_batch_row', sa.Column('po_total_calculated', sa.Numeric(precision=7, scale=2), nullable=True))


def downgrade():

    # purchase_batch*
    op.drop_column('purchase_batch_row', 'po_total_calculated')
    op.drop_column('purchase_batch', 'po_total_calculated')
