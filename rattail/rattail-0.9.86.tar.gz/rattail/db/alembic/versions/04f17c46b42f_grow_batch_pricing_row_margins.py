# -*- coding: utf-8; -*-
"""grow batch_pricing_row.margins

Revision ID: 04f17c46b42f
Revises: 7eb0903932ff
Create Date: 2018-11-26 18:04:14.446916

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '04f17c46b42f'
down_revision = '7eb0903932ff'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_pricing_row
    op.alter_column('batch_pricing_row', 'true_margin', type_=sa.Numeric(precision=8, scale=3))
    op.alter_column('batch_pricing_row', 'price_margin', type_=sa.Numeric(precision=8, scale=3))
    op.alter_column('batch_pricing_row', 'margin_diff', type_=sa.Numeric(precision=8, scale=3))


def downgrade():

    # batch_pricing_row
    op.alter_column('batch_pricing_row', 'true_margin', type_=sa.Numeric(precision=6, scale=3))
    op.alter_column('batch_pricing_row', 'price_margin', type_=sa.Numeric(precision=6, scale=3))
    op.alter_column('batch_pricing_row', 'margin_diff', type_=sa.Numeric(precision=6, scale=3))
