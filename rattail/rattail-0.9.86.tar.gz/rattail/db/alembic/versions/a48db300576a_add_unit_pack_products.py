# -*- coding: utf-8 -*-
"""add unit/pack products

Revision ID: a48db300576a
Revises: 3dc08453a5d3
Create Date: 2017-02-06 16:17:16.128301

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = 'a48db300576a'
down_revision = u'3dc08453a5d3'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # product
    op.drop_column('product', 'case_pack')
    op.add_column('product', sa.Column('unit_uuid', sa.String(length=32), nullable=True))
    op.add_column('product', sa.Column('pack_size', sa.Numeric(precision=9, scale=4), nullable=True))
    op.add_column('product', sa.Column('case_size', sa.Numeric(precision=9, scale=4), nullable=True))
    op.create_foreign_key(u'product_fk_unit', 'product', 'product', ['unit_uuid'], ['uuid'])


def downgrade():

    # product
    op.drop_constraint(u'product_fk_unit', 'product', type_='foreignkey')
    op.drop_column('product', 'case_size')
    op.drop_column('product', 'pack_size')
    op.drop_column('product', 'unit_uuid')
    op.add_column('product', sa.Column('case_pack', sa.INTEGER(), autoincrement=False, nullable=True))
