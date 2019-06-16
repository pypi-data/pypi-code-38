# -*- coding: utf-8 -*-
"""add batch.complete

Revision ID: 687646b42fce
Revises: 3a500dc55e0f
Create Date: 2017-07-11 15:17:17.143593

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '687646b42fce'
down_revision = u'3a500dc55e0f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch*
    op.add_column('batch_handheld', sa.Column('complete', sa.Boolean(), nullable=True))
    op.add_column('batch_inventory', sa.Column('complete', sa.Boolean(), nullable=True))
    op.add_column('batch_pricing', sa.Column('complete', sa.Boolean(), nullable=True))
    op.add_column('label_batch', sa.Column('complete', sa.Boolean(), nullable=True))
    op.add_column('vendor_catalog', sa.Column('complete', sa.Boolean(), nullable=True))
    op.add_column('vendor_invoice', sa.Column('complete', sa.Boolean(), nullable=True))


def downgrade():

    # batch*
    op.drop_column('vendor_invoice', 'complete')
    op.drop_column('vendor_catalog', 'complete')
    op.drop_column('label_batch', 'complete')
    op.drop_column('batch_pricing', 'complete')
    op.drop_column('batch_inventory', 'complete')
    op.drop_column('batch_handheld', 'complete')
