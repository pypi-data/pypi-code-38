# -*- coding: utf-8 -*-
"""add brand.confirmed

Revision ID: de4ebbf5bbb3
Revises: b82daacc86b7
Create Date: 2018-01-25 15:41:12.177378

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'de4ebbf5bbb3'
down_revision = u'b82daacc86b7'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # brand
    op.add_column('brand', sa.Column('confirmed', sa.Boolean(), nullable=True))
    op.alter_column('brand', 'name',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
    op.create_unique_constraint(u'brand_uq_name', 'brand', ['name'])


def downgrade():

    # brand
    op.drop_constraint(u'brand_uq_name', 'brand', type_='unique')
    op.alter_column('brand', 'name',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
    op.drop_column('brand', 'confirmed')
