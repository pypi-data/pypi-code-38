# -*- coding: utf-8 -*-
"""add tax

Revision ID: ee253b66b7b
Revises: 2d046576154c
Create Date: 2015-02-25 19:59:37.123167

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = 'ee253b66b7b'
down_revision = u'2d046576154c'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # tax
    op.create_table('tax',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('code', sa.Integer(), nullable=False),
                    sa.Column('description', sa.String(length=255), nullable=True),
                    sa.Column('rate', sa.Numeric(precision=7, scale=5), nullable=False),
                    sa.PrimaryKeyConstraint('uuid'),
                    sa.UniqueConstraint('code', name=u'tax_uq_code')
                    )
    op.create_table('tax_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('code', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('description', sa.String(length=255), autoincrement=False, nullable=True),
                    sa.Column('rate', sa.Numeric(precision=7, scale=5), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
                    )
    op.create_index(op.f('ix_tax_version_end_transaction_id'), 'tax_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_tax_version_operation_type'), 'tax_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_tax_version_transaction_id'), 'tax_version', ['transaction_id'], unique=False)

    # product.tax
    op.add_column(u'product', sa.Column('tax_uuid', sa.String(length=32), nullable=True))
    op.create_foreign_key(u'product_fk_tax', 'product', 'tax', ['tax_uuid'], ['uuid'])
    op.add_column(u'product_version', sa.Column('tax_uuid', sa.String(length=32), autoincrement=False, nullable=True))


def downgrade():

    # product.tax
    op.drop_column(u'product_version', 'tax_uuid')
    op.drop_constraint(u'product_fk_tax', 'product', type_='foreignkey')
    op.drop_column(u'product', 'tax_uuid')

    # tax
    op.drop_index(op.f('ix_tax_version_transaction_id'), table_name='tax_version')
    op.drop_index(op.f('ix_tax_version_operation_type'), table_name='tax_version')
    op.drop_index(op.f('ix_tax_version_end_transaction_id'), table_name='tax_version')
    op.drop_table('tax_version')
    op.drop_table('tax')
