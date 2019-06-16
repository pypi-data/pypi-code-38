# -*- coding: utf-8 -*-
"""initial schema

Revision ID: 1515aa76b64a
Revises: 
Create Date: 2015-01-21 19:34:17.767102

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '1515aa76b64a'
down_revision = None
branch_labels = ('rattail',)
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types


def upgrade():

    ####################
    # core
    ####################

    op.create_table('settings',
                    sa.Column('name', sa.String(length=255), nullable=False),
                    sa.Column('value', sa.Text(), nullable=True),
                    sa.PrimaryKeyConstraint('name')
                    )

    op.create_table('changes',
                    sa.Column('class_name', sa.String(length=25), nullable=False),
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('deleted', sa.Boolean(), nullable=True),
                    sa.PrimaryKeyConstraint('class_name', 'uuid')
                    )

    op.create_table('phone_numbers',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('parent_type', sa.String(length=20), nullable=False),
                    sa.Column('parent_uuid', sa.String(length=32), nullable=False),
                    sa.Column('preference', sa.Integer(), nullable=False),
                    sa.Column('type', sa.String(length=15), nullable=True),
                    sa.Column('number', sa.String(length=20), nullable=False),
                    sa.PrimaryKeyConstraint('uuid')
                    )

    op.create_table('email_addresses',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('parent_type', sa.String(length=20), nullable=False),
                    sa.Column('parent_uuid', sa.String(length=32), nullable=False),
                    sa.Column('preference', sa.Integer(), nullable=False),
                    sa.Column('type', sa.String(length=15), nullable=True),
                    sa.Column('address', sa.String(length=255), nullable=False),
                    sa.PrimaryKeyConstraint('uuid')
                    )

    ####################
    # people
    ####################

    op.create_table('people',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('first_name', sa.String(length=50), nullable=True),
                    sa.Column('last_name', sa.String(length=50), nullable=True),
                    sa.Column('display_name', sa.String(length=100), nullable=True),
                    sa.PrimaryKeyConstraint('uuid')
                    )

    ####################
    # users
    ####################

    op.create_table('roles',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('name', sa.String(length=25), nullable=False),
                    sa.PrimaryKeyConstraint('uuid'),
                    sa.UniqueConstraint('name', name=u'roles_uq_name')
                    )

    op.create_table('permissions',
                    sa.Column('role_uuid', sa.String(length=32), nullable=False),
                    sa.Column('permission', sa.String(length=50), nullable=False),
                    sa.ForeignKeyConstraint(['role_uuid'], [u'roles.uuid'], name=u'permissions_fk_role'),
                    sa.PrimaryKeyConstraint('role_uuid', 'permission')
                    )

    op.create_table('users',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('username', sa.String(length=25), nullable=False),
                    sa.Column('password', sa.String(length=60), nullable=True),
                    sa.Column('salt', sa.String(length=29), nullable=True),
                    sa.Column('person_uuid', sa.String(length=32), nullable=True),
                    sa.Column('active', sa.Boolean(), nullable=False),
                    sa.ForeignKeyConstraint(['person_uuid'], [u'people.uuid'], name=u'users_fk_person'),
                    sa.PrimaryKeyConstraint('uuid'),
                    sa.UniqueConstraint('username', name=u'users_uq_username')
                    )

    op.create_table('users_roles',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('user_uuid', sa.String(length=32), nullable=True),
                    sa.Column('role_uuid', sa.String(length=32), nullable=True),
                    sa.ForeignKeyConstraint(['role_uuid'], [u'roles.uuid'], name=u'users_roles_fk_role'),
                    sa.ForeignKeyConstraint(['user_uuid'], [u'users.uuid'], name=u'users_roles_fk_user'),
                    sa.PrimaryKeyConstraint('uuid')
                    )

    ####################
    # stores
    ####################

    op.create_table('stores',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('id', sa.String(length=10), nullable=True),
                    sa.Column('name', sa.String(length=100), nullable=True),
                    sa.Column('database_key', sa.String(length=30), nullable=True),
                    sa.PrimaryKeyConstraint('uuid')
                    )

    ####################
    # employees
    ####################

    op.create_table('employees',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=True),
                    sa.Column('person_uuid', sa.String(length=32), nullable=False),
                    sa.Column('status', sa.Integer(), nullable=True),
                    sa.Column('display_name', sa.String(length=100), nullable=True),
                    sa.ForeignKeyConstraint(['person_uuid'], [u'people.uuid'], name=u'employees_fk_person'),
                    sa.PrimaryKeyConstraint('uuid')
                    )

    ####################
    # customers
    ####################

    op.create_table('customers',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('id', sa.String(length=20), nullable=True),
                    sa.Column('name', sa.String(length=255), nullable=True),
                    sa.Column('email_preference', sa.Integer(), nullable=True),
                    sa.PrimaryKeyConstraint('uuid')
                    )

    op.create_table('customer_groups',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('id', sa.String(length=20), nullable=True),
                    sa.Column('name', sa.String(length=255), nullable=True),
                    sa.PrimaryKeyConstraint('uuid')
                    )

    op.create_table('customers_groups',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('customer_uuid', sa.String(length=32), nullable=False),
                    sa.Column('group_uuid', sa.String(length=32), nullable=False),
                    sa.Column('ordinal', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['customer_uuid'], [u'customers.uuid'], name=u'customers_groups_fk_customer'),
                    sa.ForeignKeyConstraint(['group_uuid'], [u'customer_groups.uuid'], name=u'customers_groups_fk_group'),
                    sa.PrimaryKeyConstraint('uuid')
                    )

    op.create_table('customers_people',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('customer_uuid', sa.String(length=32), nullable=False),
                    sa.Column('person_uuid', sa.String(length=32), nullable=False),
                    sa.Column('ordinal', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['customer_uuid'], [u'customers.uuid'], name=u'customers_people_fk_customer'),
                    sa.ForeignKeyConstraint(['person_uuid'], [u'people.uuid'], name=u'customers_people_fk_person'),
                    sa.PrimaryKeyConstraint('uuid')
                    )

    ####################
    # vendors
    ####################

    op.create_table('vendors',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('id', sa.String(length=15), nullable=True),
                    sa.Column('name', sa.String(length=40), nullable=True),
                    sa.Column('special_discount', sa.Numeric(precision=5, scale=3), nullable=True),
                    sa.PrimaryKeyConstraint('uuid'),
                    sa.UniqueConstraint('id', name=u'vendors_uq_id')
                    )

    op.create_table('vendor_contacts',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('vendor_uuid', sa.String(length=32), nullable=False),
                    sa.Column('person_uuid', sa.String(length=32), nullable=False),
                    sa.Column('preference', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['person_uuid'], [u'people.uuid'], name=u'vendor_contacts_fk_person'),
                    sa.ForeignKeyConstraint(['vendor_uuid'], [u'vendors.uuid'], name=u'vendor_contacts_fk_vendor'),
                    sa.PrimaryKeyConstraint('uuid')
                    )

    ####################
    # org
    ####################

    op.create_table('departments',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('number', sa.Integer(), nullable=True),
                    sa.Column('name', sa.String(length=30), nullable=True),
                    sa.PrimaryKeyConstraint('uuid')
                    )

    op.create_table('subdepartments',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('number', sa.Integer(), nullable=True),
                    sa.Column('name', sa.String(length=30), nullable=True),
                    sa.Column('department_uuid', sa.String(length=32), nullable=True),
                    sa.ForeignKeyConstraint(['department_uuid'], [u'departments.uuid'], name=u'subdepartments_fk_department'),
                    sa.PrimaryKeyConstraint('uuid')
                    )

    op.create_table('categories',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('number', sa.Integer(), nullable=True),
                    sa.Column('name', sa.String(length=50), nullable=True),
                    sa.Column('department_uuid', sa.String(length=32), nullable=True),
                    sa.ForeignKeyConstraint(['department_uuid'], [u'departments.uuid'], name=u'categories_fk_department'),
                    sa.PrimaryKeyConstraint('uuid')
                    )

    op.create_table('families',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('code', sa.Integer(), nullable=True),
                    sa.Column('name', sa.String(length=50), nullable=True),
                    sa.PrimaryKeyConstraint('uuid')
                    )

    op.create_table('report_codes',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('code', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=50), nullable=True),
                    sa.PrimaryKeyConstraint('uuid', name=u'report_codes_pk_uuid'),
                    sa.UniqueConstraint('code', name=u'report_codes_uq_code')
                    )

    ####################
    # products
    ####################

    op.create_table('brands',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('name', sa.String(length=100), nullable=True),
                    sa.PrimaryKeyConstraint('uuid')
                    )

    op.create_table('products',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('upc', rattail.db.types.GPCType(), nullable=True),
                    sa.Column('department_uuid', sa.String(length=32), nullable=True),
                    sa.Column('subdepartment_uuid', sa.String(length=32), nullable=True),
                    sa.Column('category_uuid', sa.String(length=32), nullable=True),
                    sa.Column('family_uuid', sa.String(length=32), nullable=True),
                    sa.Column('report_code_uuid', sa.String(length=32), nullable=True),
                    sa.Column('brand_uuid', sa.String(length=32), nullable=True),
                    sa.Column('description', sa.String(length=60), nullable=True),
                    sa.Column('description2', sa.String(length=60), nullable=True),
                    sa.Column('size', sa.String(length=30), nullable=True),
                    sa.Column('unit_of_measure', sa.String(length=4), nullable=True),
                    sa.Column('not_for_sale', sa.Boolean(), nullable=False),
                    sa.Column('regular_price_uuid', sa.String(length=32), nullable=True),
                    sa.Column('current_price_uuid', sa.String(length=32), nullable=True),
                    sa.ForeignKeyConstraint(['brand_uuid'], [u'brands.uuid'], name=u'products_fk_brand'),
                    sa.ForeignKeyConstraint(['category_uuid'], [u'categories.uuid'], name=u'products_fk_category'),
                    sa.ForeignKeyConstraint(['department_uuid'], [u'departments.uuid'], name=u'products_fk_department'),
                    sa.ForeignKeyConstraint(['family_uuid'], [u'families.uuid'], name=u'products_fk_family'),
                    sa.ForeignKeyConstraint(['report_code_uuid'], [u'report_codes.uuid'], name=u'products_fk_report_code'),
                    sa.ForeignKeyConstraint(['subdepartment_uuid'], [u'subdepartments.uuid'], name=u'products_fk_subdepartment'),
                    sa.PrimaryKeyConstraint('uuid')
                    )
    op.create_index('products_ix_upc', 'products', ['upc'], unique=False)

    op.create_table('product_codes',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('product_uuid', sa.String(length=32), nullable=False),
                    sa.Column('ordinal', sa.Integer(), nullable=False),
                    sa.Column('code', sa.String(length=20), nullable=True),
                    sa.ForeignKeyConstraint(['product_uuid'], [u'products.uuid'], name=u'product_codes_fk_product'),
                    sa.PrimaryKeyConstraint('uuid')
                    )

    op.create_table('product_costs',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('product_uuid', sa.String(length=32), nullable=False),
                    sa.Column('vendor_uuid', sa.String(length=32), nullable=False),
                    sa.Column('preference', sa.Integer(), nullable=False),
                    sa.Column('code', sa.String(length=15), nullable=True),
                    sa.Column('case_size', sa.Integer(), nullable=True),
                    sa.Column('case_cost', sa.Numeric(precision=9, scale=5), nullable=True),
                    sa.Column('pack_size', sa.Integer(), nullable=True),
                    sa.Column('pack_cost', sa.Numeric(precision=9, scale=5), nullable=True),
                    sa.Column('unit_cost', sa.Numeric(precision=9, scale=5), nullable=True),
                    sa.Column('effective', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['product_uuid'], [u'products.uuid'], name=u'product_costs_fk_product'),
                    sa.ForeignKeyConstraint(['vendor_uuid'], [u'vendors.uuid'], name=u'product_costs_fk_vendor'),
                    sa.PrimaryKeyConstraint('uuid')
                    )

    op.create_table('product_prices',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('product_uuid', sa.String(length=32), nullable=False),
                    sa.Column('type', sa.Integer(), nullable=True),
                    sa.Column('level', sa.Integer(), nullable=True),
                    sa.Column('starts', sa.DateTime(), nullable=True),
                    sa.Column('ends', sa.DateTime(), nullable=True),
                    sa.Column('price', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.Column('multiple', sa.Integer(), nullable=True),
                    sa.Column('pack_price', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.Column('pack_multiple', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['product_uuid'], [u'products.uuid'], name=u'product_prices_fk_product'),
                    sa.PrimaryKeyConstraint('uuid')
                    )
    op.create_foreign_key(u'products_regular_price_uuid_fkey', 'products', 'product_prices', ['regular_price_uuid'], ['uuid'])
    op.create_foreign_key(u'products_current_price_uuid_fkey', 'products', 'product_prices', ['current_price_uuid'], ['uuid'])

    ####################
    # batches
    ####################

    op.create_table('batches',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('provider', sa.String(length=50), nullable=True),
                    sa.Column('id', sa.String(length=8), nullable=True),
                    sa.Column('source', sa.String(length=6), nullable=True),
                    sa.Column('destination', sa.String(length=6), nullable=True),
                    sa.Column('action_type', sa.String(length=6), nullable=True),
                    sa.Column('description', sa.String(length=50), nullable=True),
                    sa.Column('rowcount', sa.Integer(), nullable=True),
                    sa.Column('executed', sa.DateTime(), nullable=True),
                    sa.Column('purge', sa.Date(), nullable=True),
                    sa.PrimaryKeyConstraint('uuid')
                    )

    op.create_table('batch_columns',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('batch_uuid', sa.String(length=32), nullable=True),
                    sa.Column('ordinal', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=20), nullable=True),
                    sa.Column('display_name', sa.String(length=50), nullable=True),
                    sa.Column('sil_name', sa.String(length=10), nullable=True),
                    sa.Column('data_type', sa.String(length=15), nullable=True),
                    sa.Column('description', sa.String(length=50), nullable=True),
                    sa.Column('visible', sa.Boolean(), nullable=True),
                    sa.ForeignKeyConstraint(['batch_uuid'], [u'batches.uuid'], name=u'batch_columns_fk_batch'),
                    sa.PrimaryKeyConstraint('uuid')
                    )

    ####################
    # labels
    ####################

    op.create_table('label_profiles',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('ordinal', sa.Integer(), nullable=True),
                    sa.Column('code', sa.String(length=3), nullable=True),
                    sa.Column('description', sa.String(length=50), nullable=True),
                    sa.Column('printer_spec', sa.String(length=255), nullable=True),
                    sa.Column('formatter_spec', sa.String(length=255), nullable=True),
                    sa.Column('format', sa.Text(), nullable=True),
                    sa.Column('visible', sa.Boolean(), nullable=True),
                    sa.PrimaryKeyConstraint('uuid')
                    )

    ####################
    # vendor catalogs
    ####################

    op.create_table('vendor_catalog',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('created', sa.DateTime(), nullable=False),
                    sa.Column('created_by_uuid', sa.String(length=32), nullable=False),
                    sa.Column('cognized', sa.DateTime(), nullable=True),
                    sa.Column('cognized_by_uuid', sa.String(length=32), nullable=True),
                    sa.Column('rowcount', sa.Integer(), nullable=True),
                    sa.Column('executed', sa.DateTime(), nullable=True),
                    sa.Column('executed_by_uuid', sa.String(length=32), nullable=True),
                    sa.Column('purge', sa.Date(), nullable=True),
                    sa.Column('filename', sa.String(length=255), nullable=False),
                    sa.Column('parser_key', sa.String(length=100), nullable=False),
                    sa.Column('vendor_uuid', sa.String(length=32), nullable=False),
                    sa.Column('effective', sa.Date(), nullable=True),
                    sa.ForeignKeyConstraint(['cognized_by_uuid'], [u'users.uuid'], name=u'vendor_catalog_fk_cognized_by'),
                    sa.ForeignKeyConstraint(['created_by_uuid'], [u'users.uuid'], name=u'vendor_catalog_fk_created_by'),
                    sa.ForeignKeyConstraint(['executed_by_uuid'], [u'users.uuid'], name=u'vendor_catalog_fk_executed_by'),
                    sa.ForeignKeyConstraint(['vendor_uuid'], [u'vendors.uuid'], name=u'vendor_catalog_fk_vendor'),
                    sa.PrimaryKeyConstraint('uuid')
                    )
    op.create_table('vendor_catalog_row',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('batch_uuid', sa.String(length=32), nullable=False),
                    sa.Column('sequence', sa.Integer(), nullable=False),
                    sa.Column('status_code', sa.Integer(), nullable=True),
                    sa.Column('removed', sa.Boolean(), nullable=False),
                    sa.Column('upc', rattail.db.types.GPCType(), nullable=True),
                    sa.Column('product_uuid', sa.String(length=32), nullable=True),
                    sa.Column('vendor_code', sa.String(length=30), nullable=True),
                    sa.Column('brand_name', sa.String(length=100), nullable=True),
                    sa.Column('description', sa.String(length=255), nullable=False),
                    sa.Column('size', sa.String(length=255), nullable=True),
                    sa.Column('case_size', sa.Integer(), nullable=False),
                    sa.Column('case_cost', sa.Numeric(precision=9, scale=5), nullable=True),
                    sa.Column('unit_cost', sa.Numeric(precision=9, scale=5), nullable=True),
                    sa.Column('old_vendor_code', sa.String(length=30), nullable=True),
                    sa.Column('old_case_size', sa.Integer(), nullable=False),
                    sa.Column('old_case_cost', sa.Numeric(precision=9, scale=5), nullable=True),
                    sa.Column('old_unit_cost', sa.Numeric(precision=9, scale=5), nullable=True),
                    sa.Column('case_cost_diff', sa.Numeric(precision=9, scale=5), nullable=True),
                    sa.Column('unit_cost_diff', sa.Numeric(precision=9, scale=5), nullable=True),
                    sa.ForeignKeyConstraint(['batch_uuid'], [u'vendor_catalog.uuid'], name=u'vendor_catalog_row_fk_batch_uuid'),
                    sa.ForeignKeyConstraint(['product_uuid'], [u'products.uuid'], name=u'vendor_catalog_row_fk_product'),
                    sa.PrimaryKeyConstraint('uuid')
                    )


def downgrade():

    # vendor catalogs
    op.drop_table('vendor_catalog_row')
    op.drop_table('vendor_catalog')

    # labels
    op.drop_table('label_profiles')

    # batches
    op.drop_table('batch_columns')
    op.drop_table('batches')

    # products
    op.drop_constraint(u'products_current_price_uuid_fkey', 'products', type_='foreignkey')
    op.drop_constraint(u'products_regular_price_uuid_fkey', 'products', type_='foreignkey')
    op.drop_table('product_prices')
    op.drop_table('product_costs')
    op.drop_table('product_codes')
    op.drop_index('products_ix_upc', table_name='products')
    op.drop_table('products')
    op.drop_table('brands')

    # org
    op.drop_table('report_codes')
    op.drop_table('families')
    op.drop_table('categories')
    op.drop_table('subdepartments')
    op.drop_table('departments')

    # vendors
    op.drop_table('vendor_contacts')
    op.drop_table('vendors')

    # customers
    op.drop_table('customers_people')
    op.drop_table('customers_groups')
    op.drop_table('customer_groups')
    op.drop_table('customers')

    # employees
    op.drop_table('employees')

    # stores
    op.drop_table('stores')

    # users
    op.drop_table('users_roles')
    op.drop_table('users')
    op.drop_table('permissions')
    op.drop_table('roles')

    # people
    op.drop_table('people')

    # contact
    op.drop_table('email_addresses')
    op.drop_table('phone_numbers')

    # core
    op.drop_table('changes')
    op.drop_table('settings')
