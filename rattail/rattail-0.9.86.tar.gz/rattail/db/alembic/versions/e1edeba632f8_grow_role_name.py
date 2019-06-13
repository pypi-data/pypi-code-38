# -*- coding: utf-8; -*-
"""grow role.name

Revision ID: e1edeba632f8
Revises: 11a9145414a9
Create Date: 2018-11-13 10:46:53.014681

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'e1edeba632f8'
down_revision = '11a9145414a9'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # role
    op.alter_column('role', 'name', type_=sa.String(length=100))


def downgrade():

    # role
    op.alter_column('role', 'name', type_=sa.String(length=25))
