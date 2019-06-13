# -*- coding: utf-8 -*-
"""add department flags

Revision ID: e63d53698e9f
Revises: 37e0e46ec6fe
Create Date: 2017-10-30 20:36:02.800556

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'e63d53698e9f'
down_revision = u'37e0e46ec6fe'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # department
    op.add_column('department', sa.Column('personnel', sa.Boolean(), nullable=True))
    op.add_column('department', sa.Column('product', sa.Boolean(), nullable=True))
    op.add_column('department_version', sa.Column('personnel', sa.Boolean(), autoincrement=False, nullable=True))
    op.add_column('department_version', sa.Column('product', sa.Boolean(), autoincrement=False, nullable=True))


def downgrade():

    # department
    op.drop_column('department_version', 'product')
    op.drop_column('department_version', 'personnel')
    op.drop_column('department', 'product')
    op.drop_column('department', 'personnel')
