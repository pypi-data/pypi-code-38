# -*- coding: utf-8; -*-
"""add label_profile.sync_me

Revision ID: f7dc4e92752c
Revises: 648cb088658c
Create Date: 2018-12-04 18:19:19.927787

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'f7dc4e92752c'
down_revision = '648cb088658c'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # label_profile
    op.add_column('label_profile', sa.Column('sync_me', sa.Boolean(), nullable=True))
    op.add_column('label_profile_version', sa.Column('sync_me', sa.Boolean(), autoincrement=False, nullable=True))


def downgrade():

    # label_profile
    op.drop_column('label_profile_version', 'sync_me')
    op.drop_column('label_profile', 'sync_me')
