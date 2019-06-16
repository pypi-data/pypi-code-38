# -*- coding: utf-8 -*-
"""add deposit_link

Revision ID: 2d046576154c
Revises: 3f5be78f0f18
Create Date: 2015-02-25 01:13:20.181621

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '2d046576154c'
down_revision = u'3f5be78f0f18'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # deposit_link
    op.create_table('deposit_link',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('code', sa.Integer(), nullable=False),
                    sa.Column('description', sa.String(length=255), nullable=True),
                    sa.Column('amount', sa.Numeric(precision=5, scale=2), nullable=False),
                    sa.PrimaryKeyConstraint('uuid'),
                    sa.UniqueConstraint('code', name=u'deposit_link_uq_code')
                    )
    op.create_table('deposit_link_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('code', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('description', sa.String(length=255), autoincrement=False, nullable=True),
                    sa.Column('amount', sa.Numeric(precision=5, scale=2), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
                    )
    op.create_index(op.f('ix_deposit_link_version_end_transaction_id'), 'deposit_link_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_deposit_link_version_operation_type'), 'deposit_link_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_deposit_link_version_transaction_id'), 'deposit_link_version', ['transaction_id'], unique=False)

    # product.deposit_link
    op.add_column(u'product', sa.Column('deposit_link_uuid', sa.String(length=32), nullable=True))
    op.create_foreign_key(u'product_fk_deposit_link', 'product', 'deposit_link', ['deposit_link_uuid'], ['uuid'])
    op.add_column(u'product_version', sa.Column('deposit_link_uuid', sa.String(length=32), autoincrement=False, nullable=True))


def downgrade():

    # product.deposit_link
    op.drop_column(u'product_version', 'deposit_link_uuid')
    op.drop_constraint(u'product_fk_deposit_link', 'product', type_='foreignkey')
    op.drop_column(u'product', 'deposit_link_uuid')

    # deposit_link
    op.drop_index(op.f('ix_deposit_link_version_transaction_id'), table_name='deposit_link_version')
    op.drop_index(op.f('ix_deposit_link_version_operation_type'), table_name='deposit_link_version')
    op.drop_index(op.f('ix_deposit_link_version_end_transaction_id'), table_name='deposit_link_version')
    op.drop_table('deposit_link_version')
    op.drop_table('deposit_link')
