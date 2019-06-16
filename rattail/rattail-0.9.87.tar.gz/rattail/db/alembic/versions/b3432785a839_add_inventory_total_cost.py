# -*- coding: utf-8; -*-
"""add inventory total cost

Revision ID: b3432785a839
Revises: fd935205655d
Create Date: 2017-07-19 00:22:04.784889

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'b3432785a839'
down_revision = u'fd935205655d'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_inventory
    op.add_column('batch_inventory', sa.Column('total_cost', sa.Numeric(precision=9, scale=5), nullable=True))
    op.add_column('batch_inventory_row', sa.Column('total_cost', sa.Numeric(precision=9, scale=5), nullable=True))


def downgrade():

    # batch_inventory
    op.drop_column('batch_inventory_row', 'total_cost')
    op.drop_column('batch_inventory', 'total_cost')
