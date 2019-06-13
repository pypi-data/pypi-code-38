# -*- coding: utf-8 -*-
"""add user events

Revision ID: 1242c7a0e24a
Revises: cc3de1ca0689
Create Date: 2017-08-04 16:41:40.837455

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '1242c7a0e24a'
down_revision = u'cc3de1ca0689'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # user_event
    op.create_table('user_event',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('user_uuid', sa.String(length=32), nullable=False),
                    sa.Column('type_code', sa.Integer(), nullable=False),
                    sa.Column('occurred', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['user_uuid'], [u'user.uuid'], name=u'user_x_role_fk_user'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # user_event
    op.drop_table('user_event')
