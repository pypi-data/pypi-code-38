# -*- coding: utf-8 -*-
"""add bouncer

Revision ID: 35b1da3be8f5
Revises: 3623367c499f
Create Date: 2015-07-21 18:12:24.027137

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '35b1da3be8f5'
down_revision = u'3623367c499f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # email_bounce
    op.create_table('email_bounce',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('config_key', sa.String(length=20), nullable=False),
                    sa.Column('bounced', sa.DateTime(), nullable=False),
                    sa.Column('bounce_recipient_address', sa.String(length=255), nullable=False),
                    sa.Column('intended_recipient_address', sa.String(length=255), nullable=True),
                    sa.Column('intended_recipient_key', sa.String(length=20), nullable=True),
                    sa.Column('processed', sa.DateTime(), nullable=True),
                    sa.Column('processed_by_uuid', sa.String(length=32), nullable=True),
                    sa.ForeignKeyConstraint(['processed_by_uuid'], [u'user.uuid'], name=u'email_bounce_fk_processed_by'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # email_bounce
    op.drop_table('email_bounce')
