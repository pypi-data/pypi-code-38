# -*- coding: utf-8; -*-
"""add product status

Revision ID: a9b37b388e56
Revises: b3432785a839
Create Date: 2017-07-19 02:33:27.081113

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'a9b37b388e56'
down_revision = u'b3432785a839'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # product
    op.add_column('product', sa.Column('status_code', sa.Integer(), nullable=True))
    op.add_column('product_version', sa.Column('status_code', sa.Integer(), autoincrement=False, nullable=True))


def downgrade():

    # product
    op.drop_column('product_version', 'status_code')
    op.drop_column('product', 'status_code')
