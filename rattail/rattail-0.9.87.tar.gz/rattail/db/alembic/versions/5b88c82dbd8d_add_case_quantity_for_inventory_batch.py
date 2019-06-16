# -*- coding: utf-8 -*-
"""add case_quantity for inventory batch

Revision ID: 5b88c82dbd8d
Revises: 687646b42fce
Create Date: 2017-07-11 18:59:11.901199

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '5b88c82dbd8d'
down_revision = u'687646b42fce'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_inventory
    op.add_column('batch_inventory_row', sa.Column('case_quantity', sa.Numeric(precision=6, scale=2), nullable=True))


def downgrade():

    # batch_inventory
    op.drop_column('batch_inventory_row', 'case_quantity')
