# -*- coding: utf-8 -*-
"""add customer.active_in_pos_sticky

Revision ID: cc3de1ca0689
Revises: a9b37b388e56
Create Date: 2017-08-04 11:06:15.835698

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = 'cc3de1ca0689'
down_revision = u'a9b37b388e56'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # customer
    op.add_column('customer', sa.Column('active_in_pos_sticky', sa.Boolean(), nullable=True))
    op.add_column('customer_version', sa.Column('active_in_pos_sticky', sa.Boolean(), autoincrement=False, nullable=True))
    customer = sa.sql.table('customer', sa.sql.column('active_in_pos_sticky'))
    op.execute(customer.update().values({'active_in_pos_sticky': False}))
    op.alter_column('customer', 'active_in_pos_sticky', nullable=False)


def downgrade():

    # customer
    op.drop_column('customer_version', 'active_in_pos_sticky')
    op.drop_column('customer', 'active_in_pos_sticky')
