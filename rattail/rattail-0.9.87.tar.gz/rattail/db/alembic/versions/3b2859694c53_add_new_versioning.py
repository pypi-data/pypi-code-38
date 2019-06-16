# -*- coding: utf-8 -*-
"""add new versioning

Revision ID: 3b2859694c53
Revises: e9fca3d787ea
Create Date: 2017-05-25 18:28:45.492796

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '3b2859694c53'
down_revision = u'e9fca3d787ea'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # transaction
    op.create_table('transaction',
                    sa.Column('issued_at', sa.DateTime(), nullable=True),
                    sa.Column('id', sa.BigInteger(), nullable=False),
                    sa.Column('remote_addr', sa.String(length=50), nullable=True),
                    sa.Column('user_id', sa.String(length=32), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], [u'user.uuid'], ),
                    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transaction_user_id'), 'transaction', ['user_id'], unique=False)

    # person_version
    op.create_table('person_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('first_name', sa.String(length=50), autoincrement=False, nullable=True),
                    sa.Column('middle_name', sa.String(length=50), autoincrement=False, nullable=True),
                    sa.Column('last_name', sa.String(length=50), autoincrement=False, nullable=True),
                    sa.Column('display_name', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_person_version_end_transaction_id'), 'person_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_person_version_operation_type'), 'person_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_person_version_transaction_id'), 'person_version', ['transaction_id'], unique=False)


def downgrade():

    # person
    op.drop_index(op.f('ix_person_version_transaction_id'), table_name='person_version')
    op.drop_index(op.f('ix_person_version_operation_type'), table_name='person_version')
    op.drop_index(op.f('ix_person_version_end_transaction_id'), table_name='person_version')
    op.drop_table('person_version')

    # transaction
    op.drop_index(op.f('ix_transaction_user_id'), table_name='transaction')
    op.drop_table('transaction')
