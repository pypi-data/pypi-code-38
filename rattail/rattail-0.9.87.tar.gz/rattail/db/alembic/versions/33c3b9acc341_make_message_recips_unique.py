# -*- coding: utf-8 -*-
"""make message recips unique

Revision ID: 33c3b9acc341
Revises: 6e6d6e2ef0e
Create Date: 2016-02-11 17:42:19.561486

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '33c3b9acc341'
down_revision = u'6e6d6e2ef0e'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # message_recip
    op.create_unique_constraint(u'message_recip_uq_message_recipient', 'message_recip', ['message_uuid', 'recipient_uuid'])


def downgrade():

    # message_recip
    op.drop_constraint(u'message_recip_uq_message_recipient', 'message_recip', type_='unique')
