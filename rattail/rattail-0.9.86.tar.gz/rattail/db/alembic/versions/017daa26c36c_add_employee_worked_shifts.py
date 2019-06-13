# -*- coding: utf-8 -*-
"""add employee worked shifts

Revision ID: 017daa26c36c
Revises: 33c3b9acc341
Create Date: 2016-04-25 14:58:32.182768

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '017daa26c36c'
down_revision = u'33c3b9acc341'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # employee_shift_worked
    op.create_table('employee_shift_worked',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('employee_uuid', sa.String(length=32), nullable=False),
                    sa.Column('store_uuid', sa.String(length=32), nullable=True),
                    sa.Column('punch_in', sa.DateTime(), nullable=True),
                    sa.Column('punch_out', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['employee_uuid'], [u'employee.uuid'], name=u'employee_shift_worked_fk_employee'),
                    sa.ForeignKeyConstraint(['store_uuid'], [u'store.uuid'], name=u'employee_shift_worked_fk_store'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # employee_shift_worked
    op.drop_table('employee_shift_worked')
