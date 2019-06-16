# -*- coding: utf-8 -*-
"""add members

Revision ID: f3781f071de3
Revises: 45b90e4f8ab4
Create Date: 2018-12-19 21:46:02.335362

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'f3781f071de3'
down_revision = '45b90e4f8ab4'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # member
    op.create_table('member',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('id', sa.String(length=20), nullable=True),
                    sa.Column('person_uuid', sa.String(length=32), nullable=True),
                    sa.Column('customer_uuid', sa.String(length=32), nullable=True),
                    sa.Column('joined', sa.Date(), nullable=True),
                    sa.Column('active', sa.Boolean(), nullable=False),
                    sa.Column('equity_current', sa.Boolean(), nullable=True),
                    sa.Column('equity_total', sa.Numeric(precision=5, scale=2), nullable=True),
                    sa.Column('equity_payment_due', sa.Date(), nullable=True),
                    sa.Column('equity_last_paid', sa.Date(), nullable=True),
                    sa.Column('equity_payment_credit', sa.Numeric(precision=5, scale=2), nullable=False),
                    sa.Column('withdrew', sa.Date(), nullable=True),
                    sa.ForeignKeyConstraint(['customer_uuid'], ['customer.uuid'], name='member_fk_customer'),
                    sa.ForeignKeyConstraint(['person_uuid'], ['person.uuid'], name='member_fk_person'),
                    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_table('member_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('id', sa.String(length=20), autoincrement=False, nullable=True),
                    sa.Column('person_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('customer_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('joined', sa.Date(), autoincrement=False, nullable=True),
                    sa.Column('active', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('equity_current', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('equity_total', sa.Numeric(precision=5, scale=2), autoincrement=False, nullable=True),
                    sa.Column('equity_payment_due', sa.Date(), autoincrement=False, nullable=True),
                    sa.Column('equity_last_paid', sa.Date(), autoincrement=False, nullable=True),
                    sa.Column('equity_payment_credit', sa.Numeric(precision=5, scale=2), autoincrement=False, nullable=True),
                    sa.Column('withdrew', sa.Date(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_member_version_end_transaction_id'), 'member_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_member_version_operation_type'), 'member_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_member_version_transaction_id'), 'member_version', ['transaction_id'], unique=False)


def downgrade():

    # member
    op.drop_index(op.f('ix_member_version_transaction_id'), table_name='member_version')
    op.drop_index(op.f('ix_member_version_operation_type'), table_name='member_version')
    op.drop_index(op.f('ix_member_version_end_transaction_id'), table_name='member_version')
    op.drop_table('member_version')
    op.drop_table('member')
