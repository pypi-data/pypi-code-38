# -*- coding: utf-8; -*-
"""add newproduct batch

Revision ID: 4e5526fae79e
Revises: 5b393c108673
Create Date: 2019-04-16 17:39:49.902316

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '4e5526fae79e'
down_revision = '5b393c108673'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_newproduct
    op.create_table('batch_newproduct',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('description', sa.String(length=255), nullable=True),
                    sa.Column('created', sa.DateTime(), nullable=False),
                    sa.Column('created_by_uuid', sa.String(length=32), nullable=False),
                    sa.Column('cognized', sa.DateTime(), nullable=True),
                    sa.Column('cognized_by_uuid', sa.String(length=32), nullable=True),
                    sa.Column('rowcount', sa.Integer(), nullable=True),
                    sa.Column('complete', sa.Boolean(), nullable=False),
                    sa.Column('executed', sa.DateTime(), nullable=True),
                    sa.Column('executed_by_uuid', sa.String(length=32), nullable=True),
                    sa.Column('purge', sa.Date(), nullable=True),
                    sa.Column('notes', sa.Text(), nullable=True),
                    sa.Column('extra_data', sa.Text(), nullable=True),
                    sa.Column('status_code', sa.Integer(), nullable=True),
                    sa.Column('status_text', sa.String(length=255), nullable=True),
                    sa.Column('input_filename', sa.String(length=255), nullable=True),
                    sa.ForeignKeyConstraint(['cognized_by_uuid'], ['user.uuid'], name='batch_newproduct_fk_cognized_by'),
                    sa.ForeignKeyConstraint(['created_by_uuid'], ['user.uuid'], name='batch_newproduct_fk_created_by'),
                    sa.ForeignKeyConstraint(['executed_by_uuid'], ['user.uuid'], name='batch_newproduct_fk_executed_by'),
                    sa.PrimaryKeyConstraint('uuid')
    )

    # batch_newproduct_row
    op.create_table('batch_newproduct_row',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('batch_uuid', sa.String(length=32), nullable=False),
                    sa.Column('sequence', sa.Integer(), nullable=False),
                    sa.Column('status_code', sa.Integer(), nullable=True),
                    sa.Column('status_text', sa.String(length=255), nullable=True),
                    sa.Column('modified', sa.DateTime(), nullable=True),
                    sa.Column('removed', sa.Boolean(), nullable=False),
                    sa.Column('item_entry', sa.String(length=20), nullable=True),
                    sa.Column('upc', rattail.db.types.GPCType(), nullable=True),
                    sa.Column('item_id', sa.String(length=20), nullable=True),
                    sa.Column('product_uuid', sa.String(length=32), nullable=True),
                    sa.Column('brand_name', sa.String(length=100), nullable=True),
                    sa.Column('description', sa.String(length=255), nullable=True),
                    sa.Column('size', sa.String(length=255), nullable=True),
                    sa.Column('department_number', sa.Integer(), nullable=True),
                    sa.Column('department_name', sa.String(length=30), nullable=True),
                    sa.Column('subdepartment_number', sa.Integer(), nullable=True),
                    sa.Column('subdepartment_name', sa.String(length=30), nullable=True),
                    sa.Column('vendor_id', sa.String(length=15), nullable=True),
                    sa.Column('vendor_uuid', sa.String(length=32), nullable=True),
                    sa.Column('vendor_item_code', sa.String(length=20), nullable=True),
                    sa.Column('department_uuid', sa.String(length=32), nullable=True),
                    sa.Column('subdepartment_uuid', sa.String(length=32), nullable=True),
                    sa.Column('case_size', sa.Numeric(precision=9, scale=4), nullable=True),
                    sa.Column('case_cost', sa.Numeric(precision=10, scale=5), nullable=True),
                    sa.Column('unit_cost', sa.Numeric(precision=10, scale=5), nullable=True),
                    sa.Column('regular_price', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.Column('regular_price_multiple', sa.Integer(), nullable=True),
                    sa.Column('pack_price', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.Column('pack_price_multiple', sa.Integer(), nullable=True),
                    sa.Column('suggested_price', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.Column('category_code', sa.String(length=20), nullable=True),
                    sa.Column('category_uuid', sa.String(length=32), nullable=True),
                    sa.Column('family_code', sa.Integer(), nullable=True),
                    sa.Column('family_uuid', sa.String(length=32), nullable=True),
                    sa.Column('report_code', sa.Integer(), nullable=True),
                    sa.Column('report_uuid', sa.String(length=32), nullable=True),
                    sa.Column('brand_uuid', sa.String(length=32), nullable=True),
                    sa.ForeignKeyConstraint(['batch_uuid'], ['batch_newproduct.uuid'], name='batch_newproduct_row_fk_batch'),
                    sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'], name='batch_newproduct_row_fk_product'),
                    sa.ForeignKeyConstraint(['vendor_uuid'], ['vendor.uuid'], name='batch_newproduct_row_fk_vendor'),
                    sa.ForeignKeyConstraint(['department_uuid'], ['department.uuid'], name='batch_newproduct_row_fk_department'),
                    sa.ForeignKeyConstraint(['subdepartment_uuid'], ['subdepartment.uuid'], name='batch_newproduct_row_fk_subdepartment'),
                    sa.ForeignKeyConstraint(['category_uuid'], ['category.uuid'], name='batch_newproduct_row_fk_category'),
                    sa.ForeignKeyConstraint(['family_uuid'], ['family.uuid'], name='batch_newproduct_row_fk_family'),
                    sa.ForeignKeyConstraint(['report_uuid'], ['report_code.uuid'], name='batch_newproduct_row_fk_report'),
                    sa.ForeignKeyConstraint(['brand_uuid'], ['brand.uuid'], name='batch_newproduct_row_fk_brand'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # batch_newproduct*
    op.drop_table('batch_newproduct_row')
    op.drop_table('batch_newproduct')
