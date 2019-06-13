# -*- coding: utf-8; -*-
"""add receiving.truck_dump_children_first

Revision ID: 40a4855cb22d
Revises: 4db5dbf725f5
Create Date: 2019-02-05 11:37:03.807392

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '40a4855cb22d'
down_revision = '4db5dbf725f5'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # purchase_batch
    op.add_column('purchase_batch', sa.Column('truck_dump_children_first', sa.Boolean(), nullable=True))
    op.add_column('purchase_batch', sa.Column('truck_dump_ready', sa.Boolean(), nullable=True))


def downgrade():

    # purchase_batch
    op.drop_column('purchase_batch', 'truck_dump_ready')
    op.drop_column('purchase_batch', 'truck_dump_children_first')
