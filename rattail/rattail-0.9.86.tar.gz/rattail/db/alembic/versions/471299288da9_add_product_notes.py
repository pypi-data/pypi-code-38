# -*- coding: utf-8 -*-
"""add product.notes

Revision ID: 471299288da9
Revises: 234c79420312
Create Date: 2017-02-27 15:33:20.114167

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '471299288da9'
down_revision = u'234c79420312'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # product
    op.add_column('product', sa.Column('ingredients', sa.Text(), nullable=True))
    op.add_column('product', sa.Column('notes', sa.Text(), nullable=True))


def downgrade():

    # product
    op.drop_column('product', 'notes')
    op.drop_column('product', 'ingredients')
