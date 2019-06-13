# -*- coding: utf-8 -*-
"""grow inventory_row.total_cost

Revision ID: d67dee1cb849
Revises: 51756b0edcdf
Create Date: 2018-07-09 13:45:55.702987

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'd67dee1cb849'
down_revision = u'51756b0edcdf'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_inventory_row
    op.alter_column('batch_inventory_row', 'total_cost', type_=sa.Numeric(precision=12, scale=5))


def downgrade():

    # batch_inventory_row
    op.alter_column('batch_inventory_row', 'total_cost', type_=sa.Numeric(precision=9, scale=5))
