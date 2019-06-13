# -*- coding: utf-8; -*-
"""add purchase_batch.order_quantities_known

Revision ID: be079e974a52
Revises: 8b02c6eaf318
Create Date: 2018-07-17 20:16:57.863186

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'be079e974a52'
down_revision = '8b02c6eaf318'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # purchase_batch
    op.add_column('purchase_batch', sa.Column('order_quantities_known', sa.Boolean(), nullable=True))


def downgrade():

    # purchase_batch
    op.drop_column('purchase_batch', 'order_quantities_known')
