# -*- coding: utf-8 -*-
"""add label_batch.filename

Revision ID: 19da5ebe6fb5
Revises: 36ffa8b83782
Create Date: 2016-11-19 15:59:36.893529

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '19da5ebe6fb5'
down_revision = u'36ffa8b83782'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


batch_id_seq = sa.Sequence('batch_id_seq')


def upgrade():

    # label_batch
    op.add_column('label_batch', sa.Column('filename', sa.String(length=255), nullable=True))


def downgrade():

    # label_batch
    op.drop_column('label_batch', 'filename')
