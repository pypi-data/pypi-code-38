# -*- coding: utf-8 -*-
"""grow report code name

Revision ID: 6cadbeb3f82
Revises: 321f8f7b3887
Create Date: 2015-03-02 19:30:55.679551

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '6cadbeb3f82'
down_revision = u'321f8f7b3887'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():
    op.alter_column('report_code', 'name', type_=sa.String(length=100))


def downgrade():
    op.alter_column('report_code', 'name', type_=sa.String(length=50))
