# -*- coding: utf-8 -*-
"""add Email.invalid flag

Revision ID: 4da3fe4a368f
Revises: 14d23631733d
Create Date: 2015-12-17 11:10:56.104030

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '4da3fe4a368f'
down_revision = u'14d23631733d'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # email
    op.add_column('email', sa.Column('invalid', sa.Boolean(), nullable=True))


def downgrade():

    # email
    op.drop_column('email', 'invalid')
