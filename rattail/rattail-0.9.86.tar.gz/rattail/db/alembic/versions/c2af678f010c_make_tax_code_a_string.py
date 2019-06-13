# -*- coding: utf-8 -*-
"""make tax code a string

Revision ID: c2af678f010c
Revises: 6a890bd49ad0
Create Date: 2017-02-06 17:40:17.486771

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = 'c2af678f010c'
down_revision = u'a48db300576a'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # tax
    op.alter_column('tax', 'code', type_=sa.String(length=30))


def downgrade():

    # tax
    op.alter_column('tax', 'code', type_=sa.Integer())
