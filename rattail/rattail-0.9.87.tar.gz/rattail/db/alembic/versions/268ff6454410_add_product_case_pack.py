# -*- coding: utf-8 -*-
"""add product.case_pack

Revision ID: 268ff6454410
Revises: 571c070b7080
Create Date: 2015-02-11 19:59:50.344482

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '268ff6454410'
down_revision = u'571c070b7080'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():
    op.add_column('product', sa.Column('case_pack', sa.Integer(), nullable=True))
    op.add_column('product_version', sa.Column('case_pack', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('product_version', 'case_pack')
    op.drop_column('product', 'case_pack')
