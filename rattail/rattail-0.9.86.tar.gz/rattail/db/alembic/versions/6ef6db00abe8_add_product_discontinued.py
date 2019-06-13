# -*- coding: utf-8 -*-
"""add product.discontinued

Revision ID: 6ef6db00abe8
Revises: 471299288da9
Create Date: 2017-03-03 12:16:42.683837

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '6ef6db00abe8'
down_revision = u'471299288da9'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # product
    op.add_column('product', sa.Column('discontinued', sa.Boolean(), nullable=True))
    product = sa.sql.table('product', sa.sql.column('discontinued'))
    op.execute(product.update().values({'discontinued': False}))
    op.alter_column('product', 'discontinued', nullable=False)


def downgrade():

    # product
    op.drop_column('product', 'discontinued')
