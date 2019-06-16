# -*- coding: utf-8 -*-
"""add role.session_timeout

Revision ID: 528c049eb5b7
Revises: d6ca20fe9452
Create Date: 2017-02-21 12:37:47.740247

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '528c049eb5b7'
down_revision = u'd6ca20fe9452'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # role
    op.add_column('role', sa.Column('session_timeout', sa.Integer(), nullable=True))


def downgrade():

    # role
    op.drop_column('role', 'session_timeout')
