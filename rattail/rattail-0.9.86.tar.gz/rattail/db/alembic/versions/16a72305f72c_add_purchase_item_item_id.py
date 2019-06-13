# -*- coding: utf-8; -*-
"""add purchase_item.item_id

Revision ID: 16a72305f72c
Revises: aa32b6e51129
Create Date: 2017-03-24 13:51:49.567407

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '16a72305f72c'
down_revision = u'aa32b6e51129'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # purchase_item
    op.add_column('purchase_item', sa.Column('item_id', sa.String(length=20), nullable=True))

    # purchase_batch_row
    op.add_column('purchase_batch_row', sa.Column('item_id', sa.String(length=20), nullable=True))


def downgrade():

    # purchase_batch_row
    op.drop_column('purchase_batch_row', 'item_id')

    # purchase_item
    op.drop_column('purchase_item', 'item_id')
