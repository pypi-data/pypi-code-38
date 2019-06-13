# -*- coding: utf-8 -*-
"""add upgrade.status

Revision ID: 139fea9de0a0
Revises: e5c3eab67b28
Create Date: 2017-08-07 19:32:43.142842

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '139fea9de0a0'
down_revision = u'e5c3eab67b28'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # upgrade
    op.add_column('upgrade', sa.Column('exit_code', sa.Integer(), nullable=True))
    op.add_column('upgrade', sa.Column('status_code', sa.Integer(), nullable=True))


def downgrade():

    # upgrade
    op.drop_column('upgrade', 'status_code')
    op.drop_column('upgrade', 'exit_code')
