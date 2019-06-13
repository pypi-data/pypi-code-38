# -*- coding: utf-8 -*-
"""add productcost.discontinued

Revision ID: 6a1ec8b93637
Revises: 3b5e0b87c176
Create Date: 2017-03-28 18:02:44.714003

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '6a1ec8b93637'
down_revision = u'3b5e0b87c176'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # product_cost
    op.add_column('product_cost', sa.Column('discontinued', sa.Boolean(), nullable=True))


def downgrade():

    # product_cost
    op.drop_column('product_cost', 'discontinued')
