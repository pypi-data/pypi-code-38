# -*- coding: utf-8 -*-
"""allow null for purchase.buyer

Revision ID: d87aeb7da072
Revises: 0174642e7b60
Create Date: 2018-05-14 12:14:23.622897

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'd87aeb7da072'
down_revision = u'0174642e7b60'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # purchase
    op.alter_column('purchase', 'buyer_uuid', existing_type=sa.VARCHAR(length=32), nullable=True)

    # purchase_batch
    op.alter_column('purchase_batch', 'buyer_uuid', existing_type=sa.VARCHAR(length=32), nullable=True)


def downgrade():

    # purchase_batch
    op.alter_column('purchase_batch', 'buyer_uuid', existing_type=sa.VARCHAR(length=32), nullable=False)

    # purchase
    op.alter_column('purchase', 'buyer_uuid', existing_type=sa.VARCHAR(length=32), nullable=False)
