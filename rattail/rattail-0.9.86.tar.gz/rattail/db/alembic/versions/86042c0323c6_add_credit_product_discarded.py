# -*- coding: utf-8 -*-
"""add credit.product_discarded

Revision ID: 86042c0323c6
Revises: a8c96f5491ae
Create Date: 2016-12-30 11:11:48.862375

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '86042c0323c6'
down_revision = u'a8c96f5491ae'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


batch_id_seq = sa.Sequence('batch_id_seq')


def upgrade():

    # purchase_batch_credit
    op.add_column('purchase_batch_credit', sa.Column('product_discarded', sa.Boolean(), nullable=True))

    # purchase_credit
    op.add_column('purchase_credit', sa.Column('product_discarded', sa.Boolean(), nullable=True))


def downgrade():

    # purchase_credit
    op.drop_column('purchase_credit', 'product_discarded')

    # purchase_batch_credit
    op.drop_column('purchase_batch_credit', 'product_discarded')
