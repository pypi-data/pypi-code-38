# -*- coding: utf-8 -*-
"""add Person.middle_name

Revision ID: 0b90d5c59fd7
Revises: 3df3144cec58
Create Date: 2016-01-07 18:51:40.499882

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '0b90d5c59fd7'
down_revision = u'3df3144cec58'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # person
    op.add_column('person', sa.Column('middle_name', sa.String(length=50), nullable=True))


def downgrade():

    # person
    op.drop_column('person', 'middle_name')
