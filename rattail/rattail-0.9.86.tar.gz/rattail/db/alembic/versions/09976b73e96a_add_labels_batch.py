# -*- coding: utf-8 -*-
"""add labels batch

Revision ID: 09976b73e96a
Revises: 9a5511fdc9f5
Create Date: 2016-11-06 16:17:14.000540

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '09976b73e96a'
down_revision = u'9a5511fdc9f5'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


batch_id_seq = sa.Sequence('batch_id_seq')


def upgrade():

    # label_batch
    op.create_table('label_batch',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('created', sa.DateTime(), nullable=False),
                    sa.Column('created_by_uuid', sa.String(length=32), nullable=False),
                    sa.Column('cognized', sa.DateTime(), nullable=True),
                    sa.Column('cognized_by_uuid', sa.String(length=32), nullable=True),
                    sa.Column('rowcount', sa.Integer(), nullable=True),
                    sa.Column('executed', sa.DateTime(), nullable=True),
                    sa.Column('executed_by_uuid', sa.String(length=32), nullable=True),
                    sa.Column('purge', sa.Date(), nullable=True),
                    sa.Column('handheld_batch_uuid', sa.String(length=32), nullable=True),
                    sa.ForeignKeyConstraint(['cognized_by_uuid'], [u'user.uuid'], name=u'label_batch_fk_cognized_by'),
                    sa.ForeignKeyConstraint(['created_by_uuid'], [u'user.uuid'], name=u'label_batch_fk_created_by'),
                    sa.ForeignKeyConstraint(['executed_by_uuid'], [u'user.uuid'], name=u'label_batch_fk_executed_by'),
                    sa.ForeignKeyConstraint(['handheld_batch_uuid'], ['batch_handheld.uuid'], name='label_batch_fk_handheld_batch'),
                    sa.PrimaryKeyConstraint('uuid')
    )

    # label_batch_row
    op.create_table('label_batch_row',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('batch_uuid', sa.String(length=32), nullable=False),
                    sa.Column('sequence', sa.Integer(), nullable=False),
                    sa.Column('status_code', sa.Integer(), nullable=True),
                    sa.Column('status_text', sa.String(length=255), nullable=True),
                    sa.Column('removed', sa.Boolean(), nullable=False),
                    sa.Column('upc', rattail.db.types.GPCType(), nullable=True),
                    sa.Column('product_uuid', sa.String(length=32), nullable=True),
                    sa.Column('brand_name', sa.String(length=100), nullable=True),
                    sa.Column('description', sa.String(length=255), nullable=True),
                    sa.Column('size', sa.String(length=255), nullable=True),
                    sa.Column('department_number', sa.Integer(), nullable=True),
                    sa.Column('department_name', sa.String(length=30), nullable=True),
                    sa.Column('label_code', sa.String(length=3), nullable=True),
                    sa.Column('label_profile_uuid', sa.String(length=32), nullable=True),
                    sa.Column('label_quantity', sa.Integer(), nullable=False),
                    sa.Column('location', sa.String(length=30), nullable=True),
                    sa.Column('category_code', sa.String(length=30), nullable=True),
                    sa.Column('category_name', sa.String(length=50), nullable=True),
                    sa.Column('description_2', sa.String(length=100), nullable=True),
                    sa.Column('regular_price', sa.Numeric(precision=6, scale=2), nullable=True),
                    sa.Column('pack_quantity', sa.Integer(), nullable=True),
                    sa.Column('pack_price', sa.Numeric(precision=6, scale=2), nullable=True),
                    sa.Column('sale_price', sa.Numeric(precision=6, scale=2), nullable=True),
                    sa.Column('sale_start', sa.DateTime(), nullable=True),
                    sa.Column('sale_stop', sa.DateTime(), nullable=True),
                    sa.Column('multi_unit_sale_price', sa.String(length=20), nullable=True),
                    sa.Column('comp_unit_size', sa.Numeric(precision=6, scale=2), nullable=True),
                    sa.Column('comp_unit_measure', sa.String(length=30), nullable=True),
                    sa.Column('comp_unit_reg_price', sa.String(length=10), nullable=True),
                    sa.Column('comp_unit_sale_price', sa.String(length=10), nullable=True),
                    sa.Column('vendor_id', sa.String(length=10), nullable=True),
                    sa.Column('vendor_name', sa.String(length=50), nullable=True),
                    sa.Column('vendor_item_code', sa.String(length=15), nullable=True),
                    sa.Column('case_quantity', sa.Numeric(precision=6, scale=2), nullable=True),
                    sa.Column('tax_code', sa.Integer(), nullable=True),
                    sa.Column('crv', sa.Boolean(), nullable=True),
                    sa.Column('organic', sa.Boolean(), nullable=True),
                    sa.Column('country_of_origin', sa.String(length=100), nullable=True),
                    sa.ForeignKeyConstraint(['batch_uuid'], [u'label_batch.uuid'], name=u'label_batch_row_fk_batch'),
                    sa.ForeignKeyConstraint(['label_profile_uuid'], [u'label_profile.uuid'], name=u'label_batch_row_fk_label_profile'),
                    sa.ForeignKeyConstraint(['product_uuid'], [u'product.uuid'], name=u'label_batch_row_fk_product'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # label_batch_row
    op.drop_table('label_batch_row')

    # label_batch
    op.drop_table('label_batch')
