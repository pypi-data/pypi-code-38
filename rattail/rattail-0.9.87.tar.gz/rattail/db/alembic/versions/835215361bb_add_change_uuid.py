# -*- coding: utf-8 -*-
"""add change uuid

Revision ID: 835215361bb
Revises: 188810a5f9db
Create Date: 2015-10-22 23:19:44.460642

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '835215361bb'
down_revision = u'188810a5f9db'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # change
    op.drop_table('change')
    op.create_table(
        'change',
        sa.Column('uuid', sa.String(length=32), nullable=False),
        sa.Column('class_name', sa.String(length=25), nullable=False),
        sa.Column('instance_uuid', sa.String(length=32), nullable=False),
        sa.Column('deleted', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # change
    op.drop_table('change')
    op.create_table(
        'change',
        sa.Column('class_name', sa.String(length=25), autoincrement=False, nullable=False),
        sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
        sa.Column('deleted', sa.Boolean(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('class_name', 'uuid', name=u'changes_pkey')
    )
