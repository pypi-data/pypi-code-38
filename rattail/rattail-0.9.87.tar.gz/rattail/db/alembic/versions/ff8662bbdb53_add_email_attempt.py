# -*- coding: utf-8; -*-
"""add email_attempt

Revision ID: ff8662bbdb53
Revises: 9f1d111fa775
Create Date: 2018-02-06 01:35:58.889529

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = 'ff8662bbdb53'
down_revision = u'9f1d111fa775'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # email_attempt
    op.create_table('email_attempt',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('key', sa.String(length=254), nullable=False),
                    sa.Column('sender', sa.Text(), nullable=False),
                    sa.Column('to', sa.Text(), nullable=False),
                    sa.Column('cc', sa.Text(), nullable=True),
                    sa.Column('bcc', sa.Text(), nullable=True),
                    sa.Column('subject', sa.String(length=254), nullable=False),
                    sa.Column('sent', sa.DateTime(), nullable=False),
                    sa.Column('status_code', sa.Integer(), nullable=False),
                    sa.Column('status_text', sa.Text(), nullable=True),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # email_attempt
    op.drop_table('email_attempt')
