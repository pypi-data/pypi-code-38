# -*- coding: utf-8 -*-
"""make employee.person unique

Revision ID: f950be5601a
Revises: 1513dc6d6ca7
Create Date: 2015-02-11 02:48:36.117822

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = 'f950be5601a'
down_revision = u'1513dc6d6ca7'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():
    op.create_unique_constraint('employee_uq_person', 'employee', ['person_uuid'])


def downgrade():
    op.drop_constraint('employee_uq_person', 'employee', type_='unique')
