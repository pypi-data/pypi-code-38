# -*- coding: utf-8; -*-
"""add dept.exempt_from_gross_sales

Revision ID: a03ee3718ff4
Revises: 05d1ed3a4a28
Create Date: 2018-06-14 11:31:36.178480

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = 'a03ee3718ff4'
down_revision = u'05d1ed3a4a28'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # department
    op.add_column('department', sa.Column('exempt_from_gross_sales', sa.Boolean(), nullable=True))
    op.add_column('department_version', sa.Column('exempt_from_gross_sales', sa.Boolean(), autoincrement=False, nullable=True))


def downgrade():

    # department
    op.drop_column('department_version', 'exempt_from_gross_sales')
    op.drop_column('department', 'exempt_from_gross_sales')
