# -*- coding: utf-8 -*-
"""add user.active_sticky

Revision ID: 3b5e0b87c176
Revises: 16a72305f72c
Create Date: 2017-03-27 21:12:29.077694

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '3b5e0b87c176'
down_revision = u'16a72305f72c'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # user
    op.add_column('user', sa.Column('active_sticky', sa.Boolean(), nullable=True))


def downgrade():

    # user
    op.drop_column('user', 'active_sticky')
