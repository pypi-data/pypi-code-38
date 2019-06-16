# -*- coding: utf-8 -*-
"""add MailingAddress

Revision ID: 3df3144cec58
Revises: 4da3fe4a368f
Create Date: 2015-12-17 18:47:37.364765

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '3df3144cec58'
down_revision = u'4da3fe4a368f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # address
    op.create_table('address',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('parent_type', sa.String(length=20), nullable=False),
                    sa.Column('parent_uuid', sa.String(length=32), nullable=False),
                    sa.Column('preference', sa.Integer(), nullable=False),
                    sa.Column('type', sa.String(length=15), nullable=True),
                    sa.Column('street', sa.String(length=100), nullable=True),
                    sa.Column('street2', sa.String(length=100), nullable=True),
                    sa.Column('city', sa.String(length=60), nullable=True),
                    sa.Column('state', sa.String(length=2), nullable=True),
                    sa.Column('zipcode', sa.String(length=10), nullable=True),
                    sa.Column('invalid', sa.Boolean(), nullable=True),
                    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_table('address_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('parent_type', sa.String(length=20), autoincrement=False, nullable=True),
                    sa.Column('parent_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('preference', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('type', sa.String(length=15), autoincrement=False, nullable=True),
                    sa.Column('street', sa.String(length=100), nullable=True),
                    sa.Column('street2', sa.String(length=100), nullable=True),
                    sa.Column('city', sa.String(length=60), nullable=True),
                    sa.Column('state', sa.String(length=2), nullable=True),
                    sa.Column('zipcode', sa.String(length=10), nullable=True),
                    sa.Column('invalid', sa.Boolean(), nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_address_version_end_transaction_id'), 'address_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_address_version_operation_type'), 'address_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_address_version_transaction_id'), 'address_version', ['transaction_id'], unique=False)


def downgrade():

    # address
    op.drop_index(op.f('ix_address_version_transaction_id'), table_name='address_version')
    op.drop_index(op.f('ix_address_version_operation_type'), table_name='address_version')
    op.drop_index(op.f('ix_address_version_end_transaction_id'), table_name='address_version')
    op.drop_table('address_version')
    op.drop_table('address')
