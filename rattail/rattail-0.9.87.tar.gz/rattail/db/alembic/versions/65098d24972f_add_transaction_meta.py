# -*- coding: utf-8 -*-
"""add transaction_meta

Revision ID: 65098d24972f
Revises: 3b2859694c53
Create Date: 2017-07-04 15:19:50.832960

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '65098d24972f'
down_revision = u'3b2859694c53'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # transaction_meta
    op.create_table('transaction_meta',
                    sa.Column('transaction_id', sa.BigInteger(), nullable=False),
                    sa.Column('key', sa.Unicode(length=255), nullable=False),
                    sa.Column('value', sa.UnicodeText(), nullable=True),
                    sa.PrimaryKeyConstraint('transaction_id', 'key')
    )


def downgrade():

    # transaction_meta
    op.drop_table('transaction_meta')
