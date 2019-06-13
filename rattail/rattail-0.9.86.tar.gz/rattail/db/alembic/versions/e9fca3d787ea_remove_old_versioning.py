# -*- coding: utf-8 -*-
"""remove old versioning

Revision ID: e9fca3d787ea
Revises: a5a7358ed27f
Create Date: 2017-05-25 17:38:12.775386

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'e9fca3d787ea'
down_revision = u'a5a7358ed27f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # *_version
    op.drop_table('label_profile_version')
    op.drop_table('customer_group_version')
    op.drop_table('product_code_version')
    op.drop_table('store_version')
    op.drop_table('address_version')
    op.drop_table('employee_version')
    op.drop_table('email_version')
    op.drop_table('customer_version')
    op.drop_table('user_version')
    op.drop_table('product_price_version')
    op.drop_table('person_version')
    op.drop_table('brand_version')
    op.drop_table('tax_version')
    op.drop_table('subdepartment_version')
    op.drop_table('department_version')
    op.drop_table('deposit_link_version')
    op.drop_table('family_version')
    op.drop_table('report_code_version')
    op.drop_table('vendor_version')
    op.drop_table('phone_version')
    op.drop_table('product_cost_version')
    op.drop_table('category_version')
    op.drop_table('role_version')
    op.drop_table('product_version')

    # transaction
    op.drop_table('transaction')


def downgrade():

    # transaction
    op.create_table('transaction',
                    sa.Column('issued_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('id', sa.BIGINT(), nullable=False),
                    sa.Column('remote_addr', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
                    sa.Column('user_uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['user_uuid'], [u'user.uuid'], name=u'transaction_user_uuid_fkey'),
                    sa.PrimaryKeyConstraint('id', name=u'transaction_pkey')
    )

    # product_version
    op.create_table('product_version',
                    sa.Column('uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
                    sa.Column('upc', sa.BIGINT(), autoincrement=False, nullable=True),
                    sa.Column('department_uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
                    sa.Column('subdepartment_uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
                    sa.Column('category_uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
                    sa.Column('family_uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
                    sa.Column('report_code_uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
                    sa.Column('brand_uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
                    sa.Column('description', sa.VARCHAR(length=60), autoincrement=False, nullable=True),
                    sa.Column('description2', sa.VARCHAR(length=60), autoincrement=False, nullable=True),
                    sa.Column('size', sa.VARCHAR(length=30), autoincrement=False, nullable=True),
                    sa.Column('unit_of_measure', sa.VARCHAR(length=4), autoincrement=False, nullable=True),
                    sa.Column('not_for_sale', sa.BOOLEAN(), autoincrement=False, nullable=True),
                    sa.Column('regular_price_uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
                    sa.Column('current_price_uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BIGINT(), autoincrement=False, nullable=True),
                    sa.Column('operation_type', sa.SMALLINT(), autoincrement=False, nullable=False),
                    sa.Column('deleted', sa.BOOLEAN(), autoincrement=False, nullable=True),
                    sa.Column('case_pack', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('organic', sa.BOOLEAN(), autoincrement=False, nullable=True),
                    sa.Column('deposit_link_uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
                    sa.Column('tax_uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
                    sa.Column('unit_size', sa.NUMERIC(precision=8, scale=3), autoincrement=False, nullable=True),
                    sa.Column('weighed', sa.BOOLEAN(), autoincrement=False, nullable=True),
                    sa.Column('discountable', sa.BOOLEAN(), autoincrement=False, nullable=True),
                    sa.Column('special_order', sa.BOOLEAN(), autoincrement=False, nullable=True),
                    sa.Column('last_sold', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id', name=u'product_version_pkey')
    )

    # role_version
    op.create_table('role_version',
                    sa.Column('uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
                    sa.Column('name', sa.VARCHAR(length=25), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BIGINT(), autoincrement=False, nullable=True),
                    sa.Column('operation_type', sa.SMALLINT(), autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id', name=u'role_version_pkey')
    )

    # category_version
    op.create_table('category_version',
                    sa.Column('uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
                    sa.Column('number', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
                    sa.Column('department_uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BIGINT(), autoincrement=False, nullable=True),
                    sa.Column('operation_type', sa.SMALLINT(), autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id', name=u'category_version_pkey')
    )

    # product_cost_version
    op.create_table('product_cost_version',
                    sa.Column('uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
                    sa.Column('product_uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
                    sa.Column('vendor_uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
                    sa.Column('preference', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('code', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
                    sa.Column('case_size', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('case_cost', sa.NUMERIC(precision=9, scale=5), autoincrement=False, nullable=True),
                    sa.Column('pack_size', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('pack_cost', sa.NUMERIC(precision=9, scale=5), autoincrement=False, nullable=True),
                    sa.Column('unit_cost', sa.NUMERIC(precision=9, scale=5), autoincrement=False, nullable=True),
                    sa.Column('effective', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BIGINT(), autoincrement=False, nullable=True),
                    sa.Column('operation_type', sa.SMALLINT(), autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id', name=u'product_cost_version_pkey')
    )

    # phone_version
    op.create_table('phone_version',
                    sa.Column('uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
                    sa.Column('parent_type', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
                    sa.Column('parent_uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
                    sa.Column('preference', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('type', sa.VARCHAR(length=15), autoincrement=False, nullable=True),
                    sa.Column('number', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BIGINT(), autoincrement=False, nullable=True),
                    sa.Column('operation_type', sa.SMALLINT(), autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id', name=u'phone_version_pkey')
    )

    # vendor_version
    op.create_table('vendor_version',
                    sa.Column('uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
                    sa.Column('id', sa.VARCHAR(length=15), autoincrement=False, nullable=True),
                    sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
                    sa.Column('special_discount', sa.NUMERIC(precision=5, scale=3), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BIGINT(), autoincrement=False, nullable=True),
                    sa.Column('operation_type', sa.SMALLINT(), autoincrement=False, nullable=False),
                    sa.Column('lead_time_days', sa.NUMERIC(precision=5, scale=1), autoincrement=False, nullable=True),
                    sa.Column('order_interval_days', sa.NUMERIC(precision=5, scale=1), autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id', name=u'vendor_version_pkey')
    )

    # report_code_version
    op.create_table('report_code_version',
                    sa.Column('uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
                    sa.Column('code', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BIGINT(), autoincrement=False, nullable=True),
                    sa.Column('operation_type', sa.SMALLINT(), autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id', name=u'report_code_version_pkey')
    )

    # family_version
    op.create_table('family_version',
                    sa.Column('uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
                    sa.Column('code', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BIGINT(), autoincrement=False, nullable=True),
                    sa.Column('operation_type', sa.SMALLINT(), autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id', name=u'family_version_pkey')
    )

    # deposit_link_version
    op.create_table('deposit_link_version',
                    sa.Column('uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
                    sa.Column('code', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('description', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
                    sa.Column('amount', sa.NUMERIC(precision=5, scale=2), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BIGINT(), autoincrement=False, nullable=True),
                    sa.Column('operation_type', sa.SMALLINT(), autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id', name=u'deposit_link_version_pkey')
    )

    # department_version
    op.create_table('department_version',
                    sa.Column('uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
                    sa.Column('number', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('name', sa.VARCHAR(length=30), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BIGINT(), autoincrement=False, nullable=True),
                    sa.Column('operation_type', sa.SMALLINT(), autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id', name=u'department_version_pkey')
    )

    # subdepartment_version
    op.create_table('subdepartment_version',
                    sa.Column('uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
                    sa.Column('number', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('name', sa.VARCHAR(length=30), autoincrement=False, nullable=True),
                    sa.Column('department_uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BIGINT(), autoincrement=False, nullable=True),
                    sa.Column('operation_type', sa.SMALLINT(), autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id', name=u'subdepartment_version_pkey')
    )

    # tax_version
    op.create_table('tax_version',
                    sa.Column('uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
                    sa.Column('code', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('description', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
                    sa.Column('rate', sa.NUMERIC(precision=7, scale=5), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BIGINT(), autoincrement=False, nullable=True),
                    sa.Column('operation_type', sa.SMALLINT(), autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id', name=u'tax_version_pkey')
    )

    # brand_version
    op.create_table('brand_version',
                    sa.Column('uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
                    sa.Column('name', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BIGINT(), autoincrement=False, nullable=True),
                    sa.Column('operation_type', sa.SMALLINT(), autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id', name=u'brand_version_pkey')
    )

    # person_version
    op.create_table('person_version',
                    sa.Column('uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
                    sa.Column('first_name', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
                    sa.Column('last_name', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
                    sa.Column('display_name', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BIGINT(), autoincrement=False, nullable=True),
                    sa.Column('operation_type', sa.SMALLINT(), autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id', name=u'person_version_pkey')
    )

    # product_price_version
    op.create_table('product_price_version',
                    sa.Column('uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
                    sa.Column('product_uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
                    sa.Column('type', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('level', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('starts', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('ends', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('price', sa.NUMERIC(precision=8, scale=3), autoincrement=False, nullable=True),
                    sa.Column('multiple', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('pack_price', sa.NUMERIC(precision=8, scale=3), autoincrement=False, nullable=True),
                    sa.Column('pack_multiple', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BIGINT(), autoincrement=False, nullable=True),
                    sa.Column('operation_type', sa.SMALLINT(), autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id', name=u'product_price_version_pkey')
    )

    # user_version
    op.create_table('user_version',
                    sa.Column('uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
                    sa.Column('username', sa.VARCHAR(length=25), autoincrement=False, nullable=True),
                    sa.Column('person_uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
                    sa.Column('active', sa.BOOLEAN(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BIGINT(), autoincrement=False, nullable=True),
                    sa.Column('operation_type', sa.SMALLINT(), autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id', name=u'user_version_pkey')
    )

    # customer_version
    op.create_table('customer_version',
                    sa.Column('uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
                    sa.Column('id', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
                    sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
                    sa.Column('email_preference', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BIGINT(), autoincrement=False, nullable=True),
                    sa.Column('operation_type', sa.SMALLINT(), autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id', name=u'customer_version_pkey')
    )

    # email_version
    op.create_table('email_version',
                    sa.Column('uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
                    sa.Column('parent_type', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
                    sa.Column('parent_uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
                    sa.Column('preference', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('type', sa.VARCHAR(length=15), autoincrement=False, nullable=True),
                    sa.Column('address', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BIGINT(), autoincrement=False, nullable=True),
                    sa.Column('operation_type', sa.SMALLINT(), autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id', name=u'email_version_pkey')
    )

    # employee_version
    op.create_table('employee_version',
                    sa.Column('uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
                    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('person_uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
                    sa.Column('status', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('display_name', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BIGINT(), autoincrement=False, nullable=True),
                    sa.Column('operation_type', sa.SMALLINT(), autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id', name=u'employee_version_pkey')
    )

    # address_version
    op.create_table('address_version',
                    sa.Column('uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
                    sa.Column('parent_type', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
                    sa.Column('parent_uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
                    sa.Column('preference', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('type', sa.VARCHAR(length=15), autoincrement=False, nullable=True),
                    sa.Column('street', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
                    sa.Column('street2', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
                    sa.Column('city', sa.VARCHAR(length=60), autoincrement=False, nullable=True),
                    sa.Column('state', sa.VARCHAR(length=2), autoincrement=False, nullable=True),
                    sa.Column('zipcode', sa.VARCHAR(length=10), autoincrement=False, nullable=True),
                    sa.Column('invalid', sa.BOOLEAN(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BIGINT(), autoincrement=False, nullable=True),
                    sa.Column('operation_type', sa.SMALLINT(), autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id', name=u'address_version_pkey')
    )

    # store_version
    op.create_table('store_version',
                    sa.Column('uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
                    sa.Column('id', sa.VARCHAR(length=10), autoincrement=False, nullable=True),
                    sa.Column('name', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
                    sa.Column('database_key', sa.VARCHAR(length=30), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BIGINT(), autoincrement=False, nullable=True),
                    sa.Column('operation_type', sa.SMALLINT(), autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id', name=u'store_version_pkey')
    )

    # product_code_version
    op.create_table('product_code_version',
                    sa.Column('uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
                    sa.Column('product_uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
                    sa.Column('ordinal', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('code', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BIGINT(), autoincrement=False, nullable=True),
                    sa.Column('operation_type', sa.SMALLINT(), autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id', name=u'product_code_version_pkey')
    )

    # customer_group_version
    op.create_table('customer_group_version',
                    sa.Column('uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
                    sa.Column('id', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
                    sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BIGINT(), autoincrement=False, nullable=True),
                    sa.Column('operation_type', sa.SMALLINT(), autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id', name=u'customer_group_version_pkey')
    )

    # label_profile_version
    op.create_table('label_profile_version',
                    sa.Column('uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
                    sa.Column('ordinal', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('code', sa.VARCHAR(length=3), autoincrement=False, nullable=True),
                    sa.Column('description', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
                    sa.Column('printer_spec', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
                    sa.Column('formatter_spec', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
                    sa.Column('format', sa.TEXT(), autoincrement=False, nullable=True),
                    sa.Column('visible', sa.BOOLEAN(), autoincrement=False, nullable=True),
                    sa.Column('transaction_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.Column('end_transaction_id', sa.BIGINT(), autoincrement=False, nullable=True),
                    sa.Column('operation_type', sa.SMALLINT(), autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('uuid', 'transaction_id', name=u'label_profile_version_pkey')
    )
