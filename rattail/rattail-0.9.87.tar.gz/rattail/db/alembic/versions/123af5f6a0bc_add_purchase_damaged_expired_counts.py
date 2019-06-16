# -*- coding: utf-8 -*-
"""add purchase damaged, expired counts

Revision ID: 123af5f6a0bc
Revises: 4bd528bca236
Create Date: 2016-12-09 14:44:04.728249

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '123af5f6a0bc'
down_revision = u'4bd528bca236'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


batch_id_seq = sa.Sequence('batch_id_seq')


def upgrade():

    # purchase_batch_row
    op.add_column('purchase_batch_row', sa.Column('cases_damaged', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('purchase_batch_row', sa.Column('cases_expired', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('purchase_batch_row', sa.Column('units_damaged', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('purchase_batch_row', sa.Column('units_expired', sa.Numeric(precision=10, scale=4), nullable=True))

    # purchase_item
    op.add_column('purchase_item', sa.Column('cases_damaged', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('purchase_item', sa.Column('cases_expired', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('purchase_item', sa.Column('units_damaged', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('purchase_item', sa.Column('units_expired', sa.Numeric(precision=10, scale=4), nullable=True))


def downgrade():

    # purchase_item
    op.drop_column('purchase_item', 'units_expired')
    op.drop_column('purchase_item', 'units_damaged')
    op.drop_column('purchase_item', 'cases_expired')
    op.drop_column('purchase_item', 'cases_damaged')

    # purchase_batch_row
    op.drop_column('purchase_batch_row', 'units_expired')
    op.drop_column('purchase_batch_row', 'units_damaged')
    op.drop_column('purchase_batch_row', 'cases_expired')
    op.drop_column('purchase_batch_row', 'cases_damaged')
