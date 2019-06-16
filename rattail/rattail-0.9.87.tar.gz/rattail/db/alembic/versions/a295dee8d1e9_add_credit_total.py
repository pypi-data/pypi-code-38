# -*- coding: utf-8 -*-
"""add credit.total

Revision ID: a295dee8d1e9
Revises: a03ee3718ff4
Create Date: 2018-06-27 15:11:54.973213

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'a295dee8d1e9'
down_revision = u'a03ee3718ff4'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # purchase_batch_credit
    op.add_column('purchase_batch_credit', sa.Column('credit_total', sa.Numeric(precision=7, scale=2), nullable=True))

    # purchase_credit
    op.add_column('purchase_credit', sa.Column('credit_total', sa.Numeric(precision=7, scale=2), nullable=True))


def downgrade():

    # purchase_credit
    op.drop_column('purchase_credit', 'credit_total')

    # purchase_batch_credit
    op.drop_column('purchase_batch_credit', 'credit_total')
