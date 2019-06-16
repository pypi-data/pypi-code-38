# -*- coding: utf-8 -*-
"""add scheduled shifts

Revision ID: b50a59f35e3f
Revises: 017daa26c36c
Create Date: 2016-04-26 18:07:55.476978

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = 'b50a59f35e3f'
down_revision = u'017daa26c36c'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # employee_shift_scheduled
    op.create_table('employee_shift_scheduled',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('employee_uuid', sa.String(length=32), nullable=False),
                    sa.Column('store_uuid', sa.String(length=32), nullable=True),
                    sa.Column('start_time', sa.DateTime(), nullable=False),
                    sa.Column('end_time', sa.DateTime(), nullable=False),
                    sa.ForeignKeyConstraint(['employee_uuid'], [u'employee.uuid'], name=u'employee_shift_scheduled_fk_employee'),
                    sa.ForeignKeyConstraint(['store_uuid'], [u'store.uuid'], name=u'employee_shift_scheduled_fk_store'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # employee_shift_scheduled
    op.drop_table('employee_shift_scheduled')
