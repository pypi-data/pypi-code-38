# -*- coding: utf-8 -*-
"""make batch filename nullable

Revision ID: 36ffa8b83782
Revises: c384c65995db
Create Date: 2016-11-16 00:58:42.069307

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '36ffa8b83782'
down_revision = u'c384c65995db'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


batch_id_seq = sa.Sequence('batch_id_seq')


def upgrade():

    # batch_handheld
    op.alter_column('batch_handheld', 'filename',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)


def downgrade():

    # batch_handheld
    op.alter_column('batch_handheld', 'filename',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
