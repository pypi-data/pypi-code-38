# -*- coding: utf-8; -*-
"""add customer.wholesale

Revision ID: 5ef33e961026
Revises: e1edeba632f8
Create Date: 2018-11-17 19:16:57.206577

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '5ef33e961026'
down_revision = u'e1edeba632f8'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # customer
    op.add_column('customer', sa.Column('wholesale', sa.Boolean(), nullable=True))
    op.add_column('customer_version', sa.Column('wholesale', sa.Boolean(), autoincrement=False, nullable=True))


def downgrade():

    # customer
    op.drop_column('customer_version', 'wholesale')
    op.drop_column('customer', 'wholesale')
