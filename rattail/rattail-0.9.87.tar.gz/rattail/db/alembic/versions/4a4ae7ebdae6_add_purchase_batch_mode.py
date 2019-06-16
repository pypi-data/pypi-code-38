# -*- coding: utf-8 -*-
"""add purchase_batch.mode

Revision ID: 4a4ae7ebdae6
Revises: 19da5ebe6fb5
Create Date: 2016-11-20 16:56:24.788146

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '4a4ae7ebdae6'
down_revision = u'19da5ebe6fb5'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql
from rattail import enum


batch_id_seq = sa.Sequence('batch_id_seq')


def upgrade():

    # purchase_batch
    op.add_column('purchase_batch', sa.Column('purchase_uuid', sa.String(length=32), nullable=True))
    op.create_foreign_key(u'purchase_batch_fk_purchase', 'purchase_batch', 'purchase', ['purchase_uuid'], ['uuid'])

    # purchase_batch.mode (provide default value then disallow null)
    op.add_column('purchase_batch', sa.Column('mode', sa.Integer(), nullable=True))
    batch = sa.sql.table('purchase_batch', sa.sql.column('mode'))
    op.execute(batch.update().values({'mode': enum.PURCHASE_BATCH_MODE_ORDERING}))
    op.alter_column('purchase_batch', 'mode', nullable=False)


def downgrade():

    # purchase_batch
    op.drop_constraint(u'purchase_batch_fk_purchase', 'purchase_batch', type_='foreignkey')
    op.drop_column('purchase_batch', 'purchase_uuid')
    op.drop_column('purchase_batch', 'mode')
