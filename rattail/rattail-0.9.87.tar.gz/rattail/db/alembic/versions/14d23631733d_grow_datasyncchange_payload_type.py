# -*- coding: utf-8 -*-
"""grow DataSyncChange.payload_type

Revision ID: 14d23631733d
Revises: 835215361bb
Create Date: 2015-11-03 16:43:31.766490

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '14d23631733d'
down_revision = u'835215361bb'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # datasync_change
    op.alter_column('datasync_change', 'payload_type', type_=sa.String(length=40))


def downgrade():

    # datasync_change
    op.alter_column('datasync_change', 'payload_type', type_=sa.String(length=20))
