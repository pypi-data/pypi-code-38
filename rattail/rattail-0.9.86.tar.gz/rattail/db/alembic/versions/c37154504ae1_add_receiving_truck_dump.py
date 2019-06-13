# -*- coding: utf-8 -*-
"""add receiving.truck_dump

Revision ID: c37154504ae1
Revises: d87aeb7da072
Create Date: 2018-05-14 12:17:21.347122

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'c37154504ae1'
down_revision = u'd87aeb7da072'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # purchase_batch
    op.add_column('purchase_batch', sa.Column('truck_dump', sa.Boolean(), nullable=True))


def downgrade():

    # purchase_batch
    op.drop_column('purchase_batch', 'truck_dump')
