# -*- coding: utf-8; -*-
"""grow datasync_change.source, consumer

Revision ID: 8b02c6eaf318
Revises: 830a20917c49
Create Date: 2018-07-10 18:55:30.539083

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '8b02c6eaf318'
down_revision = u'830a20917c49'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # datasync_change
    op.alter_column('datasync_change', 'source', type_=sa.String(length=50))
    op.alter_column('datasync_change', 'consumer', type_=sa.String(length=50))


def downgrade():

    # datasync_change
    op.alter_column('datasync_change', 'consumer', type_=sa.String(length=20))
    op.alter_column('datasync_change', 'source', type_=sa.String(length=20))
