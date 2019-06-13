# -*- coding: utf-8; -*-
"""add purchase.ship_method

Revision ID: af4c4ec011fb
Revises: ff8662bbdb53
Create Date: 2018-02-21 20:45:20.915730

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'af4c4ec011fb'
down_revision = 'ff8662bbdb53'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # purchase
    op.add_column('purchase', sa.Column('ship_method', sa.String(length=50), nullable=True))
    op.add_column('purchase', sa.Column('notes_to_vendor', sa.Text(), nullable=True))

    # purchase_batch
    op.add_column('purchase_batch', sa.Column('ship_method', sa.String(length=50), nullable=True))
    op.add_column('purchase_batch', sa.Column('notes_to_vendor', sa.Text(), nullable=True))


def downgrade():

    # purchase_batch
    op.drop_column('purchase_batch', 'notes_to_vendor')
    op.drop_column('purchase_batch', 'ship_method')

    # purchase
    op.drop_column('purchase', 'notes_to_vendor')
    op.drop_column('purchase', 'ship_method')
