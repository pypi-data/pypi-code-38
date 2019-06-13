# -*- coding: utf-8 -*-
"""grow change.class_name

Revision ID: 6e6d6e2ef0e
Revises: 27bcaa3c7f5f
Create Date: 2016-02-01 11:22:08.833707

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '6e6d6e2ef0e'
down_revision = u'27bcaa3c7f5f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # change
    op.alter_column('change', 'class_name', type_=sa.String(length=40))


def downgrade():

    # change
    op.alter_column('change', 'class_name', type_=sa.String(length=25))
