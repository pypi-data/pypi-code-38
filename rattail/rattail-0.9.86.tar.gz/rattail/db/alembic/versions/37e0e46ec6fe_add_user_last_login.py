# -*- coding: utf-8 -*-
"""add user.last_login

Revision ID: 37e0e46ec6fe
Revises: 23600f00cda7
Create Date: 2017-10-23 14:55:50.162386

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '37e0e46ec6fe'
down_revision = u'23600f00cda7'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # user
    op.add_column('user', sa.Column('last_login', sa.DateTime(), nullable=True))


def downgrade():

    # user
    op.drop_column('user', 'last_login')
