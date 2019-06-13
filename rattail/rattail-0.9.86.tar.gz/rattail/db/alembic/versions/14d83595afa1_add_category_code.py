# -*- coding: utf-8 -*-
"""add category code

Revision ID: 14d83595afa1
Revises: f5c936a4cc62
Create Date: 2016-09-28 15:45:31.331571

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '14d83595afa1'
down_revision = u'f5c936a4cc62'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


batch_id_seq = sa.Sequence('batch_id_seq')


def upgrade():

    # category
    op.add_column('category', sa.Column('code', sa.String(length=8), nullable=True))
    op.create_unique_constraint(u'category_uq_code', 'category', ['code'])


def downgrade():

    # category
    op.drop_constraint(u'category_uq_code', 'category', type_='unique')
    op.drop_column('category', 'code')
