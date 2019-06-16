# -*- coding: utf-8 -*-
"""add purchase_batch.complete

Revision ID: 8c17754a6bbf
Revises: 09976b73e96a
Create Date: 2016-11-08 11:48:52.222366

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '8c17754a6bbf'
down_revision = u'09976b73e96a'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


batch_id_seq = sa.Sequence('batch_id_seq')


def upgrade():

    # purchase_batch
    op.add_column('purchase_batch', sa.Column('complete', sa.Boolean(), nullable=True))


def downgrade():

    # purchase_batch
    op.drop_column('purchase_batch', 'complete')
