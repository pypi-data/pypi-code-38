# -*- coding: utf-8 -*-
"""add customer number

Revision ID: 195ceb6abeb3
Revises: 6a1ec8b93637
Create Date: 2017-05-11 11:29:13.525277

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '195ceb6abeb3'
down_revision = u'6a1ec8b93637'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # customer
    op.add_column('customer', sa.Column('number', sa.Integer(), nullable=True))


def downgrade():

    # customer
    op.drop_column('customer', 'number')
