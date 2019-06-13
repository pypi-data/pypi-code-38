# -*- coding: utf-8; -*-
"""add product.item_id, item_type

Revision ID: 8e965902bf93
Revises: 0a5a866f2a3d
Create Date: 2017-03-23 18:05:00.431253

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '8e965902bf93'
down_revision = u'0a5a866f2a3d'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # product
    op.add_column('product', sa.Column('item_id', sa.String(length=20), nullable=True))
    op.add_column('product', sa.Column('item_type', sa.Integer(), nullable=True))


def downgrade():

    # product
    op.drop_column('product', 'item_type')
    op.drop_column('product', 'item_id')
