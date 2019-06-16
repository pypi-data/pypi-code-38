# -*- coding: utf-8 -*-
"""add employee_x_store

Revision ID: 27bcaa3c7f5f
Revises: 57d12767eb53
Create Date: 2016-01-25 21:24:00.543909

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '27bcaa3c7f5f'
down_revision = u'57d12767eb53'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # employee_x_store
    op.create_table('employee_x_store',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('employee_uuid', sa.String(length=32), nullable=False),
                    sa.Column('store_uuid', sa.String(length=32), nullable=False),
                    sa.ForeignKeyConstraint(['employee_uuid'], [u'employee.uuid'], name=u'employee_x_store_fk_employee'),
                    sa.ForeignKeyConstraint(['store_uuid'], [u'store.uuid'], name=u'employee_x_store_fk_store'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # employee_x_store
    op.drop_table('employee_x_store')
