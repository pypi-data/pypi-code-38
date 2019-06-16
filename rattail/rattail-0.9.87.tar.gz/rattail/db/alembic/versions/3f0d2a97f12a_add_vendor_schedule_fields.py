# -*- coding: utf-8 -*-
"""add vendor schedule fields

Revision ID: 3f0d2a97f12a
Revises: 3c33f288ad62
Create Date: 2015-02-27 01:08:19.644637

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '3f0d2a97f12a'
down_revision = u'3c33f288ad62'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # vendor.lead_time_days
    op.add_column('vendor', sa.Column('lead_time_days', sa.Numeric(precision=5, scale=1), nullable=True))
    op.add_column('vendor_version', sa.Column('lead_time_days', sa.Numeric(precision=5, scale=1), autoincrement=False, nullable=True))

    # vendor.order_interval_days
    op.add_column('vendor', sa.Column('order_interval_days', sa.Numeric(precision=5, scale=1), nullable=True))
    op.add_column('vendor_version', sa.Column('order_interval_days', sa.Numeric(precision=5, scale=1), autoincrement=False, nullable=True))


def downgrade():

    # vendor.order_interval_days
    op.drop_column('vendor_version', 'order_interval_days')
    op.drop_column('vendor', 'order_interval_days')

    # vendor.lead_time_days
    op.drop_column('vendor_version', 'lead_time_days')
    op.drop_column('vendor', 'lead_time_days')
