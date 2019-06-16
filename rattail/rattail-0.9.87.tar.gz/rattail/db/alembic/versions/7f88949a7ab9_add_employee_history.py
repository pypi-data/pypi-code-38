# -*- coding: utf-8 -*-
"""add employee_history

Revision ID: 7f88949a7ab9
Revises: eb4e965ce771
Create Date: 2017-10-17 08:26:31.693081

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '7f88949a7ab9'
down_revision = u'eb4e965ce771'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # employee_history
    op.create_table('employee_history',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('employee_uuid', sa.String(length=32), nullable=False),
                    sa.Column('start_date', sa.Date(), nullable=False),
                    sa.Column('end_date', sa.Date(), nullable=True),
                    sa.ForeignKeyConstraint(['employee_uuid'], [u'employee.uuid'], name=u'employee_history_fk_employee'),
                    sa.PrimaryKeyConstraint('uuid')
    )
    op.create_table('employee_history_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('employee_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('start_date', sa.Date(), autoincrement=False, nullable=True),
                    sa.Column('end_date', sa.Date(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_employee_history_version_end_transaction_id'), 'employee_history_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_employee_history_version_operation_type'), 'employee_history_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_employee_history_version_transaction_id'), 'employee_history_version', ['transaction_id'], unique=False)


def downgrade():

    # employee_history
    op.drop_index(op.f('ix_employee_history_version_transaction_id'), table_name='employee_history_version')
    op.drop_index(op.f('ix_employee_history_version_operation_type'), table_name='employee_history_version')
    op.drop_index(op.f('ix_employee_history_version_end_transaction_id'), table_name='employee_history_version')
    op.drop_table('employee_history_version')
    op.drop_table('employee_history')
