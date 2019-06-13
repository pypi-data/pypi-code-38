# -*- coding: utf-8 -*-
"""make DepositLink.code a string

Revision ID: 09ed5bdc99f1
Revises: c2af678f010c
Create Date: 2017-02-10 00:00:49.705475

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '09ed5bdc99f1'
down_revision = u'c2af678f010c'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # deposit_link
    op.alter_column('deposit_link', 'code', type_=sa.String(length=20))


def downgrade():

    # deposit_link
    op.alter_column('deposit_link', 'code', type_=sa.Integer())
