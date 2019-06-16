# -*- coding: utf-8; -*-
"""grow pricing_batch_row.markup

Revision ID: fd7cf00b2918
Revises: f3781f071de3
Create Date: 2019-01-08 12:33:51.587887

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'fd7cf00b2918'
down_revision = 'f3781f071de3'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_pricing_row
    op.alter_column('batch_pricing_row', 'price_markup', type_=sa.Numeric(precision=5, scale=3))


def downgrade():

    # batch_pricing_row
    op.alter_column('batch_pricing_row', 'price_markup', type_=sa.Numeric(precision=4, scale=2))
