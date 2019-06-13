# -*- coding: utf-8; -*-
"""add inventory prev_on_hand

Revision ID: 1f21b32fd2a7
Revises: 139fea9de0a0
Create Date: 2017-08-09 19:01:12.534449

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '1f21b32fd2a7'
down_revision = u'139fea9de0a0'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_inventory_row
    op.add_column('batch_inventory_row', sa.Column('previous_units_on_hand', sa.Numeric(precision=10, scale=4), nullable=True))


def downgrade():

    # batch_inventory_row
    op.drop_column('batch_inventory_row', 'previous_units_on_hand')
