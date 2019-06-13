# -*- coding: utf-8 -*-
"""add employee_x_department

Revision ID: 57d12767eb53
Revises: 40326eb83e18
Create Date: 2016-01-13 21:53:29.946003

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '57d12767eb53'
down_revision = u'40326eb83e18'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # employee_x_department
    op.create_table('employee_x_department',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('employee_uuid', sa.String(length=32), nullable=False),
                    sa.Column('department_uuid', sa.String(length=32), nullable=False),
                    sa.ForeignKeyConstraint(['department_uuid'], [u'department.uuid'], name=u'employee_x_department_fk_department'),
                    sa.ForeignKeyConstraint(['employee_uuid'], [u'employee.uuid'], name=u'employee_x_department_fk_employee'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # employee_x_department
    op.drop_table('employee_x_department')
