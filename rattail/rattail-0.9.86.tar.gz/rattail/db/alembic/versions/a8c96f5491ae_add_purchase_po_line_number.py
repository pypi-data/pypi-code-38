# -*- coding: utf-8 -*-
"""add purchase.po_line_number

Revision ID: a8c96f5491ae
Revises: a47a4d73b662
Create Date: 2016-12-29 15:53:16.596495

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = 'a8c96f5491ae'
down_revision = u'a47a4d73b662'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


batch_id_seq = sa.Sequence('batch_id_seq')


def upgrade():

    # purchase_batch_row
    op.add_column('purchase_batch_row', sa.Column('po_line_number', sa.Integer(), nullable=True))

    # purchase_item
    op.add_column('purchase_item', sa.Column('po_line_number', sa.Integer(), nullable=True))


def downgrade():

    # purchase_item
    op.drop_column('purchase_item', 'po_line_number')

    # purchase_batch_row
    op.drop_column('purchase_batch_row', 'po_line_number')
