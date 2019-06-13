# -*- coding: utf-8 -*-
"""add product versioning

Revision ID: a28c3583c8f0
Revises: aa5962fb998e
Create Date: 2017-07-14 22:31:25.558644

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'a28c3583c8f0'
down_revision = u'aa5962fb998e'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # brand_version
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

    # category_version
    op.create_table('category_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('number', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('code', sa.String(length=8), autoincrement=False, nullable=True),
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

    # department_version
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

    # deposit_link_version
    op.create_table('deposit_link_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('code', sa.String(length=20), autoincrement=False, nullable=True),
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

    # employee_shift_worked_version
    op.create_table('employee_shift_worked_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('employee_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('store_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('punch_in', sa.DateTime(), autoincrement=False, nullable=True),
                    sa.Column('punch_out', sa.DateTime(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_employee_shift_worked_version_end_transaction_id'), 'employee_shift_worked_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_employee_shift_worked_version_operation_type'), 'employee_shift_worked_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_employee_shift_worked_version_transaction_id'), 'employee_shift_worked_version', ['transaction_id'], unique=False)

    # employee_x_department_version
    op.create_table('employee_x_department_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('employee_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('department_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_employee_x_department_version_end_transaction_id'), 'employee_x_department_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_employee_x_department_version_operation_type'), 'employee_x_department_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_employee_x_department_version_transaction_id'), 'employee_x_department_version', ['transaction_id'], unique=False)

    # employee_x_store_version
    op.create_table('employee_x_store_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('employee_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('store_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_employee_x_store_version_end_transaction_id'), 'employee_x_store_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_employee_x_store_version_operation_type'), 'employee_x_store_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_employee_x_store_version_transaction_id'), 'employee_x_store_version', ['transaction_id'], unique=False)

    # family_version
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

    # label_profile_version
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

    # product_code_version
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

    # product_cost_version
    op.create_table('product_cost_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('product_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('vendor_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('preference', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('code', sa.String(length=20), autoincrement=False, nullable=True),
                    sa.Column('case_size', sa.Numeric(precision=9, scale=4), autoincrement=False, nullable=True),
                    sa.Column('case_cost', sa.Numeric(precision=9, scale=5), autoincrement=False, nullable=True),
                    sa.Column('pack_size', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('pack_cost', sa.Numeric(precision=9, scale=5), autoincrement=False, nullable=True),
                    sa.Column('unit_cost', sa.Numeric(precision=9, scale=5), autoincrement=False, nullable=True),
                    sa.Column('effective', sa.DateTime(), autoincrement=False, nullable=True),
                    sa.Column('discontinued', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_product_cost_version_end_transaction_id'), 'product_cost_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_product_cost_version_operation_type'), 'product_cost_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_product_cost_version_transaction_id'), 'product_cost_version', ['transaction_id'], unique=False)

    # product_price_version
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

    # product_version
    op.create_table('product_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('upc', rattail.db.types.GPCType(), autoincrement=False, nullable=True),
                    sa.Column('scancode', sa.String(length=14), autoincrement=False, nullable=True),
                    sa.Column('item_id', sa.String(length=20), autoincrement=False, nullable=True),
                    sa.Column('item_type', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('department_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('subdepartment_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('category_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('family_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('report_code_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('deposit_link_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('tax_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('brand_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('description', sa.String(length=255), autoincrement=False, nullable=True),
                    sa.Column('description2', sa.String(length=255), autoincrement=False, nullable=True),
                    sa.Column('size', sa.String(length=30), autoincrement=False, nullable=True),
                    sa.Column('unit_size', sa.Numeric(precision=8, scale=3), autoincrement=False, nullable=True),
                    sa.Column('unit_of_measure', sa.String(length=4), autoincrement=False, nullable=True),
                    sa.Column('uom_abbreviation', sa.String(length=4), autoincrement=False, nullable=True),
                    sa.Column('weighed', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('unit_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('pack_size', sa.Numeric(precision=9, scale=4), autoincrement=False, nullable=True),
                    sa.Column('case_size', sa.Numeric(precision=9, scale=4), autoincrement=False, nullable=True),
                    sa.Column('organic', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('kosher', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('vegan', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('vegetarian', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('gluten_free', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('sugar_free', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('not_for_sale', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('discontinued', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('deleted', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('regular_price_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('current_price_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('discountable', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('special_order', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('food_stampable', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('tax1', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('tax2', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('tax3', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('ingredients', sa.Text(), autoincrement=False, nullable=True),
                    sa.Column('notes', sa.Text(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_product_version_end_transaction_id'), 'product_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_product_version_operation_type'), 'product_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_product_version_transaction_id'), 'product_version', ['transaction_id'], unique=False)

    # report_code_version
    op.create_table('report_code_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('code', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('name', sa.String(length=100), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_report_code_version_end_transaction_id'), 'report_code_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_report_code_version_operation_type'), 'report_code_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_report_code_version_transaction_id'), 'report_code_version', ['transaction_id'], unique=False)

    # role_version
    op.create_table('role_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('name', sa.String(length=25), autoincrement=False, nullable=True),
                    sa.Column('session_timeout', sa.Integer(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_role_version_end_transaction_id'), 'role_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_role_version_operation_type'), 'role_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_role_version_transaction_id'), 'role_version', ['transaction_id'], unique=False)

    # subdepartment_version
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

    # tax_version
    op.create_table('tax_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('code', sa.String(length=30), autoincrement=False, nullable=True),
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

    # user_version
    op.create_table('user_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('username', sa.String(length=25), autoincrement=False, nullable=True),
                    sa.Column('person_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('active', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('active_sticky', sa.Boolean(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_user_version_end_transaction_id'), 'user_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_user_version_operation_type'), 'user_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_user_version_transaction_id'), 'user_version', ['transaction_id'], unique=False)

    # user_x_role_version
    op.create_table('user_x_role_version',
                    sa.Column('uuid', sa.String(length=32), autoincrement=False, nullable=False),
                    sa.Column('user_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('role_uuid', sa.String(length=32), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BigInteger(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BigInteger(), nullable=True),
                    sa.Column('operation_type', sa.SmallInteger(), nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id')
    )
    op.create_index(op.f('ix_user_x_role_version_end_transaction_id'), 'user_x_role_version', ['end_transaction_id'], unique=False)
    op.create_index(op.f('ix_user_x_role_version_operation_type'), 'user_x_role_version', ['operation_type'], unique=False)
    op.create_index(op.f('ix_user_x_role_version_transaction_id'), 'user_x_role_version', ['transaction_id'], unique=False)


def downgrade():

    # user_x_role_version
    op.drop_index(op.f('ix_user_x_role_version_transaction_id'), table_name='user_x_role_version')
    op.drop_index(op.f('ix_user_x_role_version_operation_type'), table_name='user_x_role_version')
    op.drop_index(op.f('ix_user_x_role_version_end_transaction_id'), table_name='user_x_role_version')
    op.drop_table('user_x_role_version')

    # user_version
    op.drop_index(op.f('ix_user_version_transaction_id'), table_name='user_version')
    op.drop_index(op.f('ix_user_version_operation_type'), table_name='user_version')
    op.drop_index(op.f('ix_user_version_end_transaction_id'), table_name='user_version')
    op.drop_table('user_version')

    # tax_version
    op.drop_index(op.f('ix_tax_version_transaction_id'), table_name='tax_version')
    op.drop_index(op.f('ix_tax_version_operation_type'), table_name='tax_version')
    op.drop_index(op.f('ix_tax_version_end_transaction_id'), table_name='tax_version')
    op.drop_table('tax_version')

    # subdepartment_version
    op.drop_index(op.f('ix_subdepartment_version_transaction_id'), table_name='subdepartment_version')
    op.drop_index(op.f('ix_subdepartment_version_operation_type'), table_name='subdepartment_version')
    op.drop_index(op.f('ix_subdepartment_version_end_transaction_id'), table_name='subdepartment_version')
    op.drop_table('subdepartment_version')

    # role_version
    op.drop_index(op.f('ix_role_version_transaction_id'), table_name='role_version')
    op.drop_index(op.f('ix_role_version_operation_type'), table_name='role_version')
    op.drop_index(op.f('ix_role_version_end_transaction_id'), table_name='role_version')
    op.drop_table('role_version')

    # report_code_version
    op.drop_index(op.f('ix_report_code_version_transaction_id'), table_name='report_code_version')
    op.drop_index(op.f('ix_report_code_version_operation_type'), table_name='report_code_version')
    op.drop_index(op.f('ix_report_code_version_end_transaction_id'), table_name='report_code_version')
    op.drop_table('report_code_version')

    # product_version
    op.drop_index(op.f('ix_product_version_transaction_id'), table_name='product_version')
    op.drop_index(op.f('ix_product_version_operation_type'), table_name='product_version')
    op.drop_index(op.f('ix_product_version_end_transaction_id'), table_name='product_version')
    op.drop_table('product_version')

    # product_price_version
    op.drop_index(op.f('ix_product_price_version_transaction_id'), table_name='product_price_version')
    op.drop_index(op.f('ix_product_price_version_operation_type'), table_name='product_price_version')
    op.drop_index(op.f('ix_product_price_version_end_transaction_id'), table_name='product_price_version')
    op.drop_table('product_price_version')

    # product_cost_version
    op.drop_index(op.f('ix_product_cost_version_transaction_id'), table_name='product_cost_version')
    op.drop_index(op.f('ix_product_cost_version_operation_type'), table_name='product_cost_version')
    op.drop_index(op.f('ix_product_cost_version_end_transaction_id'), table_name='product_cost_version')
    op.drop_table('product_cost_version')

    # product_code_version
    op.drop_index(op.f('ix_product_code_version_transaction_id'), table_name='product_code_version')
    op.drop_index(op.f('ix_product_code_version_operation_type'), table_name='product_code_version')
    op.drop_index(op.f('ix_product_code_version_end_transaction_id'), table_name='product_code_version')
    op.drop_table('product_code_version')

    # label_profile_version
    op.drop_index(op.f('ix_label_profile_version_transaction_id'), table_name='label_profile_version')
    op.drop_index(op.f('ix_label_profile_version_operation_type'), table_name='label_profile_version')
    op.drop_index(op.f('ix_label_profile_version_end_transaction_id'), table_name='label_profile_version')
    op.drop_table('label_profile_version')

    # family_version
    op.drop_index(op.f('ix_family_version_transaction_id'), table_name='family_version')
    op.drop_index(op.f('ix_family_version_operation_type'), table_name='family_version')
    op.drop_index(op.f('ix_family_version_end_transaction_id'), table_name='family_version')
    op.drop_table('family_version')

    # employee_x_store_version
    op.drop_index(op.f('ix_employee_x_store_version_transaction_id'), table_name='employee_x_store_version')
    op.drop_index(op.f('ix_employee_x_store_version_operation_type'), table_name='employee_x_store_version')
    op.drop_index(op.f('ix_employee_x_store_version_end_transaction_id'), table_name='employee_x_store_version')
    op.drop_table('employee_x_store_version')

    # employee_x_department_version
    op.drop_index(op.f('ix_employee_x_department_version_transaction_id'), table_name='employee_x_department_version')
    op.drop_index(op.f('ix_employee_x_department_version_operation_type'), table_name='employee_x_department_version')
    op.drop_index(op.f('ix_employee_x_department_version_end_transaction_id'), table_name='employee_x_department_version')
    op.drop_table('employee_x_department_version')

    # employee_shift_worked_version
    op.drop_index(op.f('ix_employee_shift_worked_version_transaction_id'), table_name='employee_shift_worked_version')
    op.drop_index(op.f('ix_employee_shift_worked_version_operation_type'), table_name='employee_shift_worked_version')
    op.drop_index(op.f('ix_employee_shift_worked_version_end_transaction_id'), table_name='employee_shift_worked_version')
    op.drop_table('employee_shift_worked_version')

    # deposit_link_version
    op.drop_index(op.f('ix_deposit_link_version_transaction_id'), table_name='deposit_link_version')
    op.drop_index(op.f('ix_deposit_link_version_operation_type'), table_name='deposit_link_version')
    op.drop_index(op.f('ix_deposit_link_version_end_transaction_id'), table_name='deposit_link_version')
    op.drop_table('deposit_link_version')

    # department_version
    op.drop_index(op.f('ix_department_version_transaction_id'), table_name='department_version')
    op.drop_index(op.f('ix_department_version_operation_type'), table_name='department_version')
    op.drop_index(op.f('ix_department_version_end_transaction_id'), table_name='department_version')
    op.drop_table('department_version')

    # category_version
    op.drop_index(op.f('ix_category_version_transaction_id'), table_name='category_version')
    op.drop_index(op.f('ix_category_version_operation_type'), table_name='category_version')
    op.drop_index(op.f('ix_category_version_end_transaction_id'), table_name='category_version')
    op.drop_table('category_version')

    # brand_version
    op.drop_index(op.f('ix_brand_version_transaction_id'), table_name='brand_version')
    op.drop_index(op.f('ix_brand_version_operation_type'), table_name='brand_version')
    op.drop_index(op.f('ix_brand_version_end_transaction_id'), table_name='brand_version')
    op.drop_table('brand_version')
