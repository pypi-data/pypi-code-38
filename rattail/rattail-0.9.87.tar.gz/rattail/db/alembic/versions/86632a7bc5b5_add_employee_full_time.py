# -*- coding: utf-8 -*-
"""add employee.full_time

Revision ID: 86632a7bc5b5
Revises: b9658d212053
Create Date: 2017-05-16 10:39:52.906965

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '86632a7bc5b5'
down_revision = u'b9658d212053'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # employee
    op.add_column('employee', sa.Column('full_time', sa.Boolean(), nullable=True))
    op.add_column('employee', sa.Column('full_time_start', sa.Date(), nullable=True))


def downgrade():

    # employee
    # op.drop_column('employee', 'full_time_start')
    op.drop_column('employee', 'full_time')
