# -*- coding: utf-8 -*-
"""add inventory unit cost

Revision ID: aa5962fb998e
Revises: 2fe69ea73233
Create Date: 2017-07-11 22:14:31.878440

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'aa5962fb998e'
down_revision = u'2fe69ea73233'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_inventory_row
    op.add_column('batch_inventory_row', sa.Column('unit_cost', sa.Numeric(precision=9, scale=5), nullable=True))


def downgrade():

    # batch_inventory_row
    op.drop_column('batch_inventory_row', 'unit_cost')
