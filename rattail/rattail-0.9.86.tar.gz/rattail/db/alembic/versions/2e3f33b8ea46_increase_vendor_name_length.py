# -*- coding: utf-8 -*-
"""increase vendor name length

Revision ID: 2e3f33b8ea46
Revises: 1515aa76b64a
Create Date: 2015-02-05 11:29:53.537647

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '2e3f33b8ea46'
down_revision = u'1515aa76b64a'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():
    op.alter_column('vendors', 'name', type_=sa.String(length=50))


def downgrade():
    op.alter_column('vendors', 'name', type_=sa.String(length=40))
