# -*- coding: utf-8; -*-
"""add pricing_batch.true_unit_cost

Revision ID: c2085638f487
Revises: 35b451f8cc27
Create Date: 2018-11-02 18:42:35.715199

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'c2085638f487'
down_revision = '35b451f8cc27'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_pricing_row
    op.alter_column('batch_pricing_row', 'price_margin', type_=sa.Numeric(precision=6, scale=3))
    op.add_column('batch_pricing_row', sa.Column('true_margin', sa.Numeric(precision=6, scale=3), nullable=True))
    op.add_column('batch_pricing_row', sa.Column('true_unit_cost', sa.Numeric(precision=9, scale=5), nullable=True))


def downgrade():

    # batch_pricing_row
    op.drop_column('batch_pricing_row', 'true_unit_cost')
    op.drop_column('batch_pricing_row', 'true_margin')
    op.alter_column('batch_pricing_row', 'price_margin', type_=sa.Numeric(precision=5, scale=3))
