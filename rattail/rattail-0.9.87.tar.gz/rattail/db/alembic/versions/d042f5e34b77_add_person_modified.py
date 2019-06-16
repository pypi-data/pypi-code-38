# -*- coding: utf-8 -*-
"""add person.modified

Revision ID: d042f5e34b77
Revises: 0b90d5c59fd7
Create Date: 2016-01-08 11:59:24.231501

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = 'd042f5e34b77'
down_revision = u'0b90d5c59fd7'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # person
    op.add_column('person', sa.Column('modified', sa.DateTime(), nullable=True))


def downgrade():

    # person
    op.drop_column('person', 'modified')
