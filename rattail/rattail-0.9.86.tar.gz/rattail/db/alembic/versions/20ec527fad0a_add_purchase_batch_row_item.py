# -*- coding: utf-8 -*-
"""add purchase_batch_row.item

Revision ID: 20ec527fad0a
Revises: 4a4ae7ebdae6
Create Date: 2016-11-20 22:11:33.693306

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '20ec527fad0a'
down_revision = u'4a4ae7ebdae6'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


batch_id_seq = sa.Sequence('batch_id_seq')


def upgrade():

    # purchase_batch_row
    op.add_column('purchase_batch_row', sa.Column('item_uuid', sa.String(length=32), nullable=True))
    op.create_foreign_key(u'purchase_batch_row_fk_item', 'purchase_batch_row', 'purchase_item', ['item_uuid'], ['uuid'])


def downgrade():

    # purchase_batch_row
    op.drop_constraint(u'purchase_batch_row_fk_item', 'purchase_batch_row', type_='foreignkey')
    op.drop_column('purchase_batch_row', 'item_uuid')
