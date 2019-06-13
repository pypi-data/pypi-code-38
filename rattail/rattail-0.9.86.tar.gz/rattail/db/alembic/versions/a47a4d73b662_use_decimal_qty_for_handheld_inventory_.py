# -*- coding: utf-8 -*-
"""use decimal qty for handheld/inventory rows

Revision ID: a47a4d73b662
Revises: 0f4cb39da3cc
Create Date: 2016-12-16 16:12:48.505269

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = 'a47a4d73b662'
down_revision = u'0f4cb39da3cc'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


batch_id_seq = sa.Sequence('batch_id_seq')


def upgrade():

    # batch_handheld_row
    op.alter_column('batch_handheld_row', 'cases', type_=sa.Numeric(precision=10, scale=4))
    op.alter_column('batch_handheld_row', 'units', type_=sa.Numeric(precision=10, scale=4))

    # batch_inventory_row
    op.alter_column('batch_inventory_row', 'cases', type_=sa.Numeric(precision=10, scale=4))
    op.alter_column('batch_inventory_row', 'units', type_=sa.Numeric(precision=10, scale=4))


def downgrade():

    # batch_inventory_row
    op.alter_column('batch_inventory_row', 'cases', type_=sa.Integer())
    op.alter_column('batch_inventory_row', 'units', type_=sa.Integer())

    # batch_handheld_row
    op.alter_column('batch_handheld_row', 'cases', type_=sa.Integer())
    op.alter_column('batch_handheld_row', 'units', type_=sa.Integer())
