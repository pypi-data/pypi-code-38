# -*- coding: utf-8 -*-
"""add datasync change

Revision ID: 188810a5f9db
Revises: 3a7029aed67
Create Date: 2015-10-17 01:07:39.015318

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '188810a5f9db'
down_revision = u'3a7029aed67'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():
    op.create_table('datasync_change',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('source', sa.String(length=20), nullable=False),
                    sa.Column('payload_type', sa.String(length=20), nullable=False),
                    sa.Column('payload_key', sa.String(length=50), nullable=False),
                    sa.Column('deletion', sa.Boolean(), nullable=False),
                    sa.Column('obtained', sa.DateTime(), nullable=False),
                    sa.Column('consumer', sa.String(length=20), nullable=True),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():
    op.drop_table('datasync_change')
