# -*- coding: utf-8 -*-
"""add versioning

Revision ID: 47d30c955111
Revises: 33b76c3cb892
Create Date: 2015-02-07 12:55:40.293606

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '47d30c955111'
down_revision = u'33b76c3cb892'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types


def upgrade():

    connection = op.get_bind()

    # transaction
    op.create_table('transaction',
                    sa.Column('issued_at', sa.DateTime(), nullable=True),
                    sa.Column('id', sa.BigInteger(), nullable=False),
                    sa.Column('remote_addr', sa.String(length=50), nullable=True),
                    sa.Column('user_uuid', sa.String(length=32), nullable=True),
                    sa.ForeignKeyConstraint(['user_uuid'], ['user.uuid'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_transaction_user_uuid'), 'transaction', ['user_uuid'], unique=False)

    # email
    op.create_table('email_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('parent_type', sa.String(length=20), autoincrement=False, nullable=True),
                    sa.Column('parent_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('preference', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('type', sa.String(length=15), autoincrement=False, nullable=True),
                    sa.Column('address', sa.String(length=255), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
                    )
    op.create_index(op.f('ix_email_version_end_transaction_id'), 'email_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_email_version_operation_type'), 'email_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_email_version_transaction_id'), 'email_version', ['transaction_id'], unique=False)

    # phone
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

    # person
    op.create_table('person_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('first_name', sa.String(length=50), autoincrement=False, nullable=True),
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

    # role
    op.create_table('role_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('name', sa.String(length=25), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
                    )
    op.create_index(op.f('ix_role_version_end_transaction_id'), 'role_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_role_version_operation_type'), 'role_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_role_version_transaction_id'), 'role_version', ['transaction_id'], unique=False)

    # user
    op.create_table('user_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('username', sa.String(length=25), autoincrement=False, nullable=True),
                    sa.Column('person_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('active', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
                    )
    op.create_index(op.f('ix_user_version_end_transaction_id'), 'user_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_user_version_operation_type'), 'user_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_user_version_transaction_id'), 'user_version', ['transaction_id'], unique=False)

    # store
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

    # employee
    op.create_table('employee_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('id', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('person_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('status', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('display_name', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
                    )
    op.create_index(op.f('ix_employee_version_end_transaction_id'), 'employee_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_employee_version_operation_type'), 'employee_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_employee_version_transaction_id'), 'employee_version', ['transaction_id'], unique=False)

    # customer_group
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

    # customer
    op.create_table('customer_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('id', sa.String(length=20), autoincrement=False, nullable=True),
                    sa.Column('name', sa.String(length=255), autoincrement=False, nullable=True),
                    sa.Column('email_preference', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
                    )
    op.create_index(op.f('ix_customer_version_end_transaction_id'), 'customer_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_customer_version_operation_type'), 'customer_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_customer_version_transaction_id'), 'customer_version', ['transaction_id'], unique=False)

    # vendor
    op.create_table('vendor_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('id', sa.String(length=15), autoincrement=False, nullable=True),
                    sa.Column('name', sa.String(length=50), autoincrement=False, nullable=True),
                    sa.Column('special_discount', sa.Numeric(precision=5, scale=3), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
                    )
    op.create_index(op.f('ix_vendor_version_end_transaction_id'), 'vendor_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_vendor_version_operation_type'), 'vendor_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_vendor_version_transaction_id'), 'vendor_version', ['transaction_id'], unique=False)

    # department
    op.create_table('department_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('number', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('name', sa.String(length=30), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
                    )
    op.create_index(op.f('ix_department_version_end_transaction_id'), 'department_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_department_version_operation_type'), 'department_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_department_version_transaction_id'), 'department_version', ['transaction_id'], unique=False)

    # subdepartment
    op.create_table('subdepartment_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('number', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('name', sa.String(length=30), autoincrement=False, nullable=True),
                    sa.Column('department_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
                    )
    op.create_index(op.f('ix_subdepartment_version_end_transaction_id'), 'subdepartment_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_subdepartment_version_operation_type'), 'subdepartment_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_subdepartment_version_transaction_id'), 'subdepartment_version', ['transaction_id'], unique=False)

    # category
    op.create_table('category_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('number', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('name', sa.String(length=50), autoincrement=False, nullable=True),
                    sa.Column('department_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
                    )
    op.create_index(op.f('ix_category_version_end_transaction_id'), 'category_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_category_version_operation_type'), 'category_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_category_version_transaction_id'), 'category_version', ['transaction_id'], unique=False)

    # family
    op.create_table('family_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('code', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('name', sa.String(length=50), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
                    )
    op.create_index(op.f('ix_family_version_end_transaction_id'), 'family_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_family_version_operation_type'), 'family_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_family_version_transaction_id'), 'family_version', ['transaction_id'], unique=False)

    # report_code
    op.create_table('report_code_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('code', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('name', sa.String(length=50), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
                    )
    op.create_index(op.f('ix_report_code_version_end_transaction_id'), 'report_code_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_report_code_version_operation_type'), 'report_code_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_report_code_version_transaction_id'), 'report_code_version', ['transaction_id'], unique=False)

    # brand
    op.create_table('brand_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('name', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
                    )
    op.create_index(op.f('ix_brand_version_end_transaction_id'), 'brand_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_brand_version_operation_type'), 'brand_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_brand_version_transaction_id'), 'brand_version', ['transaction_id'], unique=False)

    # product
    op.create_table('product_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('upc', rattail.db.types.GPCType(), autoincrement=False, nullable=True),
                    sa.Column('department_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('subdepartment_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('category_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('family_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('report_code_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('brand_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('description', sa.String(length=60), autoincrement=False, nullable=True),
                    sa.Column('description2', sa.String(length=60), autoincrement=False, nullable=True),
                    sa.Column('size', sa.String(length=30), autoincrement=False, nullable=True),
                    sa.Column('unit_of_measure', sa.String(length=4), autoincrement=False, nullable=True),
                    sa.Column('not_for_sale', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('regular_price_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('current_price_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
                    )
    op.create_index(op.f('ix_product_version_end_transaction_id'), 'product_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_product_version_operation_type'), 'product_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_product_version_transaction_id'), 'product_version', ['transaction_id'], unique=False)

    # product_code
    op.create_table('product_code_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('product_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('ordinal', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('code', sa.String(length=20), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
                    )
    op.create_index(op.f('ix_product_code_version_end_transaction_id'), 'product_code_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_product_code_version_operation_type'), 'product_code_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_product_code_version_transaction_id'), 'product_code_version', ['transaction_id'], unique=False)

    # product_cost
    op.create_table('product_cost_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('product_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('vendor_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('preference', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('code', sa.String(length=15), autoincrement=False, nullable=True),
                    sa.Column('case_size', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('case_cost', sa.Numeric(precision=9, scale=5), autoincrement=False, nullable=True),
                    sa.Column('pack_size', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('pack_cost', sa.Numeric(precision=9, scale=5), autoincrement=False, nullable=True),
                    sa.Column('unit_cost', sa.Numeric(precision=9, scale=5), autoincrement=False, nullable=True),
                    sa.Column('effective', sa.DateTime(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
                    )
    op.create_index(op.f('ix_product_cost_version_end_transaction_id'), 'product_cost_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_product_cost_version_operation_type'), 'product_cost_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_product_cost_version_transaction_id'), 'product_cost_version', ['transaction_id'], unique=False)

    # product_price
    op.create_table('product_price_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('product_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('type', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('level', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('starts', sa.DateTime(), autoincrement=False, nullable=True),
                    sa.Column('ends', sa.DateTime(), autoincrement=False, nullable=True),
                    sa.Column('price', sa.Numeric(precision=8, scale=3), autoincrement=False, nullable=True),
                    sa.Column('multiple', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('pack_price', sa.Numeric(precision=8, scale=3), autoincrement=False, nullable=True),
                    sa.Column('pack_multiple', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
                    )
    op.create_index(op.f('ix_product_price_version_end_transaction_id'), 'product_price_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_product_price_version_operation_type'), 'product_price_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_product_price_version_transaction_id'), 'product_price_version', ['transaction_id'], unique=False)

    # label_profile
    op.create_table('label_profile_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('ordinal', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('code', sa.String(length=3), autoincrement=False, nullable=True),
                    sa.Column('description', sa.String(length=50), autoincrement=False, nullable=True),
                    sa.Column('printer_spec', sa.String(length=255), autoincrement=False, nullable=True),
                    sa.Column('formatter_spec', sa.String(length=255), autoincrement=False, nullable=True),
                    sa.Column('format', sa.Text(), autoincrement=False, nullable=True),
                    sa.Column('visible', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
                    )
    op.create_index(op.f('ix_label_profile_version_end_transaction_id'), 'label_profile_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_label_profile_version_operation_type'), 'label_profile_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_label_profile_version_transaction_id'), 'label_profile_version', ['transaction_id'], unique=False)


def downgrade():

    # label_profile
    op.drop_index(op.f('ix_label_profile_version_transaction_id'), table_name='label_profile_version')
    op.drop_index(op.f('ix_label_profile_version_operation_type'), table_name='label_profile_version')
    op.drop_index(op.f('ix_label_profile_version_end_transaction_id'), table_name='label_profile_version')
    op.drop_table('label_profile_version')

    # product_price
    op.drop_index(op.f('ix_product_price_version_transaction_id'), table_name='product_price_version')
    op.drop_index(op.f('ix_product_price_version_operation_type'), table_name='product_price_version')
    op.drop_index(op.f('ix_product_price_version_end_transaction_id'), table_name='product_price_version')
    op.drop_table('product_price_version')

    # product_cost
    op.drop_index(op.f('ix_product_cost_version_transaction_id'), table_name='product_cost_version')
    op.drop_index(op.f('ix_product_cost_version_operation_type'), table_name='product_cost_version')
    op.drop_index(op.f('ix_product_cost_version_end_transaction_id'), table_name='product_cost_version')
    op.drop_table('product_cost_version')

    # product_code
    op.drop_index(op.f('ix_product_code_version_transaction_id'), table_name='product_code_version')
    op.drop_index(op.f('ix_product_code_version_operation_type'), table_name='product_code_version')
    op.drop_index(op.f('ix_product_code_version_end_transaction_id'), table_name='product_code_version')
    op.drop_table('product_code_version')

    # product
    op.drop_index(op.f('ix_product_version_transaction_id'), table_name='product_version')
    op.drop_index(op.f('ix_product_version_operation_type'), table_name='product_version')
    op.drop_index(op.f('ix_product_version_end_transaction_id'), table_name='product_version')
    op.drop_table('product_version')

    # brand
    op.drop_index(op.f('ix_brand_version_transaction_id'), table_name='brand_version')
    op.drop_index(op.f('ix_brand_version_operation_type'), table_name='brand_version')
    op.drop_index(op.f('ix_brand_version_end_transaction_id'), table_name='brand_version')
    op.drop_table('brand_version')

    # report_code
    op.drop_index(op.f('ix_report_code_version_transaction_id'), table_name='report_code_version')
    op.drop_index(op.f('ix_report_code_version_operation_type'), table_name='report_code_version')
    op.drop_index(op.f('ix_report_code_version_end_transaction_id'), table_name='report_code_version')
    op.drop_table('report_code_version')

    # family
    op.drop_index(op.f('ix_family_version_transaction_id'), table_name='family_version')
    op.drop_index(op.f('ix_family_version_operation_type'), table_name='family_version')
    op.drop_index(op.f('ix_family_version_end_transaction_id'), table_name='family_version')
    op.drop_table('family_version')

    # category
    op.drop_index(op.f('ix_category_version_transaction_id'), table_name='category_version')
    op.drop_index(op.f('ix_category_version_operation_type'), table_name='category_version')
    op.drop_index(op.f('ix_category_version_end_transaction_id'), table_name='category_version')
    op.drop_table('category_version')

    # subdepartment
    op.drop_index(op.f('ix_subdepartment_version_transaction_id'), table_name='subdepartment_version')
    op.drop_index(op.f('ix_subdepartment_version_operation_type'), table_name='subdepartment_version')
    op.drop_index(op.f('ix_subdepartment_version_end_transaction_id'), table_name='subdepartment_version')
    op.drop_table('subdepartment_version')

    # department
    op.drop_index(op.f('ix_department_version_transaction_id'), table_name='department_version')
    op.drop_index(op.f('ix_department_version_operation_type'), table_name='department_version')
    op.drop_index(op.f('ix_department_version_end_transaction_id'), table_name='department_version')
    op.drop_table('department_version')

    # vendor
    op.drop_index(op.f('ix_vendor_version_transaction_id'), table_name='vendor_version')
    op.drop_index(op.f('ix_vendor_version_operation_type'), table_name='vendor_version')
    op.drop_index(op.f('ix_vendor_version_end_transaction_id'), table_name='vendor_version')
    op.drop_table('vendor_version')

    # customer
    op.drop_index(op.f('ix_customer_version_transaction_id'), table_name='customer_version')
    op.drop_index(op.f('ix_customer_version_operation_type'), table_name='customer_version')
    op.drop_index(op.f('ix_customer_version_end_transaction_id'), table_name='customer_version')
    op.drop_table('customer_version')

    # customer_group
    op.drop_index(op.f('ix_customer_group_version_transaction_id'), table_name='customer_group_version')
    op.drop_index(op.f('ix_customer_group_version_operation_type'), table_name='customer_group_version')
    op.drop_index(op.f('ix_customer_group_version_end_transaction_id'), table_name='customer_group_version')
    op.drop_table('customer_group_version')

    # employee
    op.drop_index(op.f('ix_employee_version_transaction_id'), table_name='employee_version')
    op.drop_index(op.f('ix_employee_version_operation_type'), table_name='employee_version')
    op.drop_index(op.f('ix_employee_version_end_transaction_id'), table_name='employee_version')
    op.drop_table('employee_version')

    # store
    op.drop_index(op.f('ix_store_version_transaction_id'), table_name='store_version')
    op.drop_index(op.f('ix_store_version_operation_type'), table_name='store_version')
    op.drop_index(op.f('ix_store_version_end_transaction_id'), table_name='store_version')
    op.drop_table('store_version')

    # user
    op.drop_index(op.f('ix_user_version_transaction_id'), table_name='user_version')
    op.drop_index(op.f('ix_user_version_operation_type'), table_name='user_version')
    op.drop_index(op.f('ix_user_version_end_transaction_id'), table_name='user_version')
    op.drop_table('user_version')

    # role
    op.drop_index(op.f('ix_role_version_transaction_id'), table_name='role_version')
    op.drop_index(op.f('ix_role_version_operation_type'), table_name='role_version')
    op.drop_index(op.f('ix_role_version_end_transaction_id'), table_name='role_version')
    op.drop_table('role_version')

    # person
    op.drop_index(op.f('ix_person_version_transaction_id'), table_name='person_version')
    op.drop_index(op.f('ix_person_version_operation_type'), table_name='person_version')
    op.drop_index(op.f('ix_person_version_end_transaction_id'), table_name='person_version')
    op.drop_table('person_version')

    # phone
    op.drop_index(op.f('ix_phone_version_transaction_id'), table_name='phone_version')
    op.drop_index(op.f('ix_phone_version_operation_type'), table_name='phone_version')
    op.drop_index(op.f('ix_phone_version_end_transaction_id'), table_name='phone_version')
    op.drop_table('phone_version')

    # email
    op.drop_index(op.f('ix_email_version_transaction_id'), table_name='email_version')
    op.drop_index(op.f('ix_email_version_operation_type'), table_name='email_version')
    op.drop_index(op.f('ix_email_version_end_transaction_id'), table_name='email_version')
    op.drop_table('email_version')

    # transaction
    op.drop_index(op.f('ix_transaction_user_uuid'), table_name='transaction')
    op.drop_table('transaction')
