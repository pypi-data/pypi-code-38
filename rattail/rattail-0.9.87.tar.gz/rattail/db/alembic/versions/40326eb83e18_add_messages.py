# -*- coding: utf-8 -*-
"""add messages

Revision ID: 40326eb83e18
Revises: d042f5e34b77
Create Date: 2016-01-11 14:08:29.612184

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '40326eb83e18'
down_revision = u'd042f5e34b77'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # message
    op.create_table('message',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('sender_uuid', sa.String(length=32), nullable=False),
                    sa.Column('subject', sa.String(length=255), nullable=True),
                    sa.Column('body', sa.Text(), nullable=True),
                    sa.Column('sent', sa.DateTime(), nullable=False),
                    sa.ForeignKeyConstraint(['sender_uuid'], [u'user.uuid'], name=u'message_fk_sender'),
                    sa.PrimaryKeyConstraint('uuid')
    )

    # message_recip
    op.create_table('message_recip',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('message_uuid', sa.String(length=32), nullable=False),
                    sa.Column('recipient_uuid', sa.String(length=32), nullable=False),
                    sa.Column('status', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['message_uuid'], [u'message.uuid'], name=u'message_recip_fk_message'),
                    sa.ForeignKeyConstraint(['recipient_uuid'], [u'user.uuid'], name=u'message_recip_fk_recipient'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # message_recip
    op.drop_table('message_recip')

    # message
    op.drop_table('message')
