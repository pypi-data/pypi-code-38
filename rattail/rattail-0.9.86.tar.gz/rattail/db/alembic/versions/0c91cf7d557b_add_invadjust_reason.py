# -*- coding: utf-8 -*-
"""add invadjust_reason

Revision ID: 0c91cf7d557b
Revises: a809caf23cf0
Create Date: 2018-01-05 18:14:18.544859

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '0c91cf7d557b'
down_revision = u'a809caf23cf0'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # invadjust_reason
    op.create_table('invadjust_reason',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('code', sa.String(length=20), nullable=False),
                    sa.Column('description', sa.String(length=255), nullable=False),
                    sa.PrimaryKeyConstraint('uuid'),
                    sa.UniqueConstraint('code', name=u'invadjust_reason_uq_code')
    )


def downgrade():

    # invadjust_reason
    op.drop_table('invadjust_reason')
