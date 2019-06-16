# -*- coding: utf-8 -*-
"""add inventory variance

Revision ID: a33583135905
Revises: b5aa18867ab3
Create Date: 2018-05-30 11:03:01.062113

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'a33583135905'
down_revision = u'b5aa18867ab3'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_inventory_row
    op.add_column('batch_inventory_row', sa.Column('variance', sa.Numeric(precision=10, scale=4), nullable=True))


def downgrade():

    # batch_inventory_row
    op.drop_column('batch_inventory_row', 'variance')
