# -*- coding: utf-8 -*-
"""add credit.vendor_item_code

Revision ID: 90a3338b187b
Revises: af4c4ec011fb
Create Date: 2018-03-01 11:23:19.029547

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '90a3338b187b'
down_revision = u'af4c4ec011fb'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # purchase_batch_credit
    op.add_column('purchase_batch_credit', sa.Column('vendor_item_code', sa.String(length=20), nullable=True))

    # purchase_credit
    op.add_column('purchase_credit', sa.Column('vendor_item_code', sa.String(length=20), nullable=True))


def downgrade():

    # purchase_credit
    op.drop_column('purchase_credit', 'vendor_item_code')

    # purchase_batch_credit
    op.drop_column('purchase_batch_credit', 'vendor_item_code')
