# -*- coding: utf-8 -*-
"""grow change key columns

Revision ID: 6c68c814f3c2
Revises: b50a59f35e3f
Create Date: 2016-05-10 21:37:09.704752

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '6c68c814f3c2'
down_revision = u'b50a59f35e3f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # change
    op.alter_column('change', 'instance_uuid', type_=sa.String(length=255))

    # datasync_change
    op.alter_column('datasync_change', 'payload_key', type_=sa.String(length=255))


def downgrade():

    # change
    op.alter_column('change', 'instance_uuid', type_=sa.String(length=32))

    # datasync_change
    op.alter_column('datasync_change', 'payload_key', type_=sa.String(length=50))
