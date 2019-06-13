# -*- coding: utf-8 -*-
"""add purchase shipped counts

Revision ID: 977a76f259bd
Revises: 92a49edc45c3
Create Date: 2018-05-16 16:06:13.691091

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '977a76f259bd'
down_revision = u'92a49edc45c3'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # purchase_batch_row
    op.add_column('purchase_batch_row', sa.Column('cases_shipped', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('purchase_batch_row', sa.Column('units_shipped', sa.Numeric(precision=10, scale=4), nullable=True))

    # purchase_item
    op.add_column('purchase_item', sa.Column('cases_shipped', sa.Numeric(precision=10, scale=4), nullable=True))
    op.add_column('purchase_item', sa.Column('units_shipped', sa.Numeric(precision=10, scale=4), nullable=True))


def downgrade():

    # purchase_item
    op.drop_column('purchase_item', 'units_shipped')
    op.drop_column('purchase_item', 'cases_shipped')

    # purchase_batch_row
    op.drop_column('purchase_batch_row', 'units_shipped')
    op.drop_column('purchase_batch_row', 'cases_shipped')
