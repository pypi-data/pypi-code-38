# -*- coding: utf-8; -*-
"""add more versions

Revision ID: 3a500dc55e0f
Revises: 65098d24972f
Create Date: 2017-07-05 13:27:45.314766

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '3a500dc55e0f'
down_revision = u'65098d24972f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # address_version
    op.create_table('address_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('parent_type', sa.String(length=20), autoincrement=False, nullable=True),
                    sa.Column('parent_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('preference', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('type', sa.String(length=15), autoincrement=False, nullable=True),
                    sa.Column('street', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('street2', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('city', sa.String(length=60), autoincrement=False, nullable=True),
                    sa.Column('state', sa.String(length=2), autoincrement=False, nullable=True),
                    sa.Column('zipcode', sa.String(length=10), autoincrement=False, nullable=True),
                    sa.Column('invalid', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_address_version_end_transaction_id'), 'address_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_address_version_operation_type'), 'address_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_address_version_transaction_id'), 'address_version', ['transaction_id'], unique=False)

    # email_version
    op.create_table('email_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('parent_type', sa.String(length=20), autoincrement=False, nullable=True),
                    sa.Column('parent_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('preference', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('type', sa.String(length=15), autoincrement=False, nullable=True),
                    sa.Column('address', sa.String(length=255), autoincrement=False, nullable=True),
                    sa.Column('invalid', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_email_version_end_transaction_id'), 'email_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_email_version_operation_type'), 'email_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_email_version_transaction_id'), 'email_version', ['transaction_id'], unique=False)

    # phone_version
    op.create_table('phone_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('parent_type', sa.String(length=20), autoincrement=False, nullable=True),
                    sa.Column('parent_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('preference', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('type', sa.String(length=15), autoincrement=False, nullable=True),
                    sa.Column('number', sa.String(length=20), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_phone_version_end_transaction_id'), 'phone_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_phone_version_operation_type'), 'phone_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_phone_version_transaction_id'), 'phone_version', ['transaction_id'], unique=False)

    # store_version
    op.create_table('store_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('id', sa.String(length=10), autoincrement=False, nullable=True),
                    sa.Column('name', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('database_key', sa.String(length=30), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_store_version_end_transaction_id'), 'store_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_store_version_operation_type'), 'store_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_store_version_transaction_id'), 'store_version', ['transaction_id'], unique=False)

    # customer_version
    op.create_table('customer_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('id', sa.String(length=20), autoincrement=False, nullable=True),
                    sa.Column('number', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('name', sa.String(length=255), autoincrement=False, nullable=True),
                    sa.Column('email_preference', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('active_in_pos', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_customer_version_end_transaction_id'), 'customer_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_customer_version_operation_type'), 'customer_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_customer_version_transaction_id'), 'customer_version', ['transaction_id'], unique=False)

    # customer_x_person_version
    op.create_table('customer_x_person_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('customer_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('person_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('ordinal', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_customer_x_person_version_end_transaction_id'), 'customer_x_person_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_customer_x_person_version_operation_type'), 'customer_x_person_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_customer_x_person_version_transaction_id'), 'customer_x_person_version', ['transaction_id'], unique=False)

    # customer_group_version
    op.create_table('customer_group_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('id', sa.String(length=20), autoincrement=False, nullable=True),
                    sa.Column('name', sa.String(length=255), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_customer_group_version_end_transaction_id'), 'customer_group_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_customer_group_version_operation_type'), 'customer_group_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_customer_group_version_transaction_id'), 'customer_group_version', ['transaction_id'], unique=False)

    # customer_x_group_version
    op.create_table('customer_x_group_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('customer_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('group_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('ordinal', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_customer_x_group_version_end_transaction_id'), 'customer_x_group_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_customer_x_group_version_operation_type'), 'customer_x_group_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_customer_x_group_version_transaction_id'), 'customer_x_group_version', ['transaction_id'], unique=False)

    # employee_version
    op.create_table('employee_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('id', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('person_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('status', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('display_name', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('full_time', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('full_time_start', sa.Date(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_employee_version_end_transaction_id'), 'employee_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_employee_version_operation_type'), 'employee_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_employee_version_transaction_id'), 'employee_version', ['transaction_id'], unique=False)

    # vendor_version
    op.create_table('vendor_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('id', sa.String(length=15), autoincrement=False, nullable=True),
                    sa.Column('name', sa.String(length=50), autoincrement=False, nullable=True),
                    sa.Column('special_discount', sa.Numeric(precision=5, scale=3), autoincrement=False, nullable=True),
                    sa.Column('lead_time_days', sa.Numeric(precision=5, scale=1), autoincrement=False, nullable=True),
                    sa.Column('order_interval_days', sa.Numeric(precision=5, scale=1), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_vendor_version_end_transaction_id'), 'vendor_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_vendor_version_operation_type'), 'vendor_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_vendor_version_transaction_id'), 'vendor_version', ['transaction_id'], unique=False)

    # vendor_contact_version
    op.create_table('vendor_contact_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('vendor_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('person_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('preference', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_vendor_contact_version_end_transaction_id'), 'vendor_contact_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_vendor_contact_version_operation_type'), 'vendor_contact_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_vendor_contact_version_transaction_id'), 'vendor_contact_version', ['transaction_id'], unique=False)


def downgrade():

    # vendor_contact_version
    op.drop_index(op.f('ix_vendor_contact_version_transaction_id'), table_name='vendor_contact_version')
    op.drop_index(op.f('ix_vendor_contact_version_operation_type'), table_name='vendor_contact_version')
    op.drop_index(op.f('ix_vendor_contact_version_end_transaction_id'), table_name='vendor_contact_version')
    op.drop_table('vendor_contact_version')

    # vendor_version
    op.drop_index(op.f('ix_vendor_version_transaction_id'), table_name='vendor_version')
    op.drop_index(op.f('ix_vendor_version_operation_type'), table_name='vendor_version')
    op.drop_index(op.f('ix_vendor_version_end_transaction_id'), table_name='vendor_version')
    op.drop_table('vendor_version')

    # employee_version
    op.drop_index(op.f('ix_employee_version_transaction_id'), table_name='employee_version')
    op.drop_index(op.f('ix_employee_version_operation_type'), table_name='employee_version')
    op.drop_index(op.f('ix_employee_version_end_transaction_id'), table_name='employee_version')
    op.drop_table('employee_version')

    # customer_x_group_version
    op.drop_index(op.f('ix_customer_x_group_version_transaction_id'), table_name='customer_x_group_version')
    op.drop_index(op.f('ix_customer_x_group_version_operation_type'), table_name='customer_x_group_version')
    op.drop_index(op.f('ix_customer_x_group_version_end_transaction_id'), table_name='customer_x_group_version')
    op.drop_table('customer_x_group_version')

    # customer_group_version
    op.drop_index(op.f('ix_customer_group_version_transaction_id'), table_name='customer_group_version')
    op.drop_index(op.f('ix_customer_group_version_operation_type'), table_name='customer_group_version')
    op.drop_index(op.f('ix_customer_group_version_end_transaction_id'), table_name='customer_group_version')
    op.drop_table('customer_group_version')

    # customer_x_person_version
    op.drop_index(op.f('ix_customer_x_person_version_transaction_id'), table_name='customer_x_person_version')
    op.drop_index(op.f('ix_customer_x_person_version_operation_type'), table_name='customer_x_person_version')
    op.drop_index(op.f('ix_customer_x_person_version_end_transaction_id'), table_name='customer_x_person_version')
    op.drop_table('customer_x_person_version')

    # customer_version
    op.drop_index(op.f('ix_customer_version_transaction_id'), table_name='customer_version')
    op.drop_index(op.f('ix_customer_version_operation_type'), table_name='customer_version')
    op.drop_index(op.f('ix_customer_version_end_transaction_id'), table_name='customer_version')
    op.drop_table('customer_version')

    # store_version
    op.drop_index(op.f('ix_store_version_transaction_id'), table_name='store_version')
    op.drop_index(op.f('ix_store_version_operation_type'), table_name='store_version')
    op.drop_index(op.f('ix_store_version_end_transaction_id'), table_name='store_version')
    op.drop_table('store_version')

    # phone_version
    op.drop_index(op.f('ix_phone_version_transaction_id'), table_name='phone_version')
    op.drop_index(op.f('ix_phone_version_operation_type'), table_name='phone_version')
    op.drop_index(op.f('ix_phone_version_end_transaction_id'), table_name='phone_version')
    op.drop_table('phone_version')

    # email_version
    op.drop_index(op.f('ix_email_version_transaction_id'), table_name='email_version')
    op.drop_index(op.f('ix_email_version_operation_type'), table_name='email_version')
    op.drop_index(op.f('ix_email_version_end_transaction_id'), table_name='email_version')
    op.drop_table('email_version')

    # address_version
    op.drop_index(op.f('ix_address_version_transaction_id'), table_name='address_version')
    op.drop_index(op.f('ix_address_version_operation_type'), table_name='address_version')
    op.drop_index(op.f('ix_address_version_end_transaction_id'), table_name='address_version')
    op.drop_table('address_version')
