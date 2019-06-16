# -*- coding: utf-8; -*-
"""add product batches

Revision ID: e1685bf9f1ad
Revises: 5dee2f796f25
Create Date: 2019-04-18 19:17:58.520577

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'e1685bf9f1ad'
down_revision = '5dee2f796f25'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_product
    op.create_table('batch_product',
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
                    sa.ForeignKeyConstraint(['cognized_by_uuid'], ['user.uuid'], name='batch_product_fk_cognized_by'),
                    sa.ForeignKeyConstraint(['created_by_uuid'], ['user.uuid'], name='batch_product_fk_created_by'),
                    sa.ForeignKeyConstraint(['executed_by_uuid'], ['user.uuid'], name='batch_product_fk_executed_by'),
                    sa.PrimaryKeyConstraint('uuid')
    )

    # batch_product_row
    op.create_table('batch_product_row',
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
                    sa.Column('department_uuid', sa.String(length=32), nullable=True),
                    sa.Column('subdepartment_uuid', sa.String(length=32), nullable=True),
                    sa.Column('vendor_uuid', sa.String(length=32), nullable=True),
                    sa.Column('vendor_item_code', sa.String(length=20), nullable=True),
                    sa.Column('regular_cost', sa.Numeric(precision=9, scale=5), nullable=True),
                    sa.Column('current_cost', sa.Numeric(precision=9, scale=5), nullable=True),
                    sa.Column('current_cost_starts', sa.DateTime(), nullable=True),
                    sa.Column('current_cost_ends', sa.DateTime(), nullable=True),
                    sa.Column('regular_price', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.Column('current_price', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.Column('current_price_starts', sa.DateTime(), nullable=True),
                    sa.Column('current_price_ends', sa.DateTime(), nullable=True),
                    sa.Column('suggested_price', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.ForeignKeyConstraint(['batch_uuid'], ['batch_product.uuid'], name='batch_product_row_fk_batch'),
                    sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'], name='batch_product_row_fk_product'),
                    sa.ForeignKeyConstraint(['department_uuid'], ['department.uuid'], name='batch_product_row_fk_department'),
                    sa.ForeignKeyConstraint(['subdepartment_uuid'], ['subdepartment.uuid'], name='batch_product_row_fk_subdepartment'),
                    sa.ForeignKeyConstraint(['vendor_uuid'], ['vendor.uuid'], name='batch_product_row_fk_vendor'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # batch_product*
    op.drop_table('batch_product_row')
    op.drop_table('batch_product')
