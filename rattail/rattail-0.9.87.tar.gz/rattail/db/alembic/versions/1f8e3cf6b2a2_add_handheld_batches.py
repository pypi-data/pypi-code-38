# -*- coding: utf-8 -*-
"""add handheld batches

Revision ID: 1f8e3cf6b2a2
Revises: 064f71d774ad
Create Date: 2016-08-16 22:16:19.088890

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '1f8e3cf6b2a2'
down_revision = u'064f71d774ad'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


batch_id_seq = sa.Sequence('batch_id_seq')


def upgrade():

    # batch_handheld
    op.create_table('batch_handheld',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('id', sa.Integer(), batch_id_seq, nullable=False),
                    sa.Column('created', sa.DateTime(), nullable=False),
                    sa.Column('created_by_uuid', sa.String(length=32), nullable=False),
                    sa.Column('cognized', sa.DateTime(), nullable=True),
                    sa.Column('cognized_by_uuid', sa.String(length=32), nullable=True),
                    sa.Column('rowcount', sa.Integer(), nullable=True),
                    sa.Column('executed', sa.DateTime(), nullable=True),
                    sa.Column('executed_by_uuid', sa.String(length=32), nullable=True),
                    sa.Column('purge', sa.Date(), nullable=True),
                    sa.Column('filename', sa.String(length=255), nullable=False),
                    sa.Column('device_type', sa.String(length=50), nullable=True),
                    sa.Column('device_name', sa.String(length=50), nullable=True),
                    sa.ForeignKeyConstraint(['cognized_by_uuid'], [u'user.uuid'], name=u'batch_handheld_fk_cognized_by'),
                    sa.ForeignKeyConstraint(['created_by_uuid'], [u'user.uuid'], name=u'batch_handheld_fk_created_by'),
                    sa.ForeignKeyConstraint(['executed_by_uuid'], [u'user.uuid'], name=u'batch_handheld_fk_executed_by'),
                    sa.PrimaryKeyConstraint('uuid')
    )

    # batch_handheld_row
    op.create_table('batch_handheld_row',
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
                    sa.Column('cases', sa.Integer(), nullable=True),
                    sa.Column('units', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['batch_uuid'], [u'batch_handheld.uuid'], name=u'batch_handheld_row_fk_batch'),
                    sa.ForeignKeyConstraint(['product_uuid'], [u'product.uuid'], name=u'batch_handheld_row_fk_product'),
                    sa.PrimaryKeyConstraint('uuid')
    )

    # batch_inventory
    op.create_table('batch_inventory',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('id', sa.Integer(), batch_id_seq, nullable=False),
                    sa.Column('created', sa.DateTime(), nullable=False),
                    sa.Column('created_by_uuid', sa.String(length=32), nullable=False),
                    sa.Column('cognized', sa.DateTime(), nullable=True),
                    sa.Column('cognized_by_uuid', sa.String(length=32), nullable=True),
                    sa.Column('rowcount', sa.Integer(), nullable=True),
                    sa.Column('executed', sa.DateTime(), nullable=True),
                    sa.Column('executed_by_uuid', sa.String(length=32), nullable=True),
                    sa.Column('purge', sa.Date(), nullable=True),
                    sa.Column('handheld_batch_uuid', sa.String(length=32), nullable=True),
                    sa.ForeignKeyConstraint(['cognized_by_uuid'], [u'user.uuid'], name=u'batch_inventory_fk_cognized_by'),
                    sa.ForeignKeyConstraint(['created_by_uuid'], [u'user.uuid'], name=u'batch_inventory_fk_created_by'),
                    sa.ForeignKeyConstraint(['executed_by_uuid'], [u'user.uuid'], name=u'batch_inventory_fk_executed_by'),
                    sa.ForeignKeyConstraint(['handheld_batch_uuid'], ['batch_handheld.uuid'], name='batch_inventory_fk_handheld_batch'),
                    sa.PrimaryKeyConstraint('uuid')
    )

    # batch_inventory_row
    op.create_table('batch_inventory_row',
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
                    sa.Column('cases', sa.Integer(), nullable=True),
                    sa.Column('units', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['batch_uuid'], [u'batch_inventory.uuid'], name=u'batch_inventory_row_fk_batch'),
                    sa.ForeignKeyConstraint(['product_uuid'], [u'product.uuid'], name=u'batch_inventory_row_fk_product'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # batch_inventory_row
    op.drop_table('batch_inventory_row')

    # batch_inventory
    op.drop_table('batch_inventory')

    # batch_handheld_row
    op.drop_table('batch_handheld_row')

    # batch_handheld
    op.drop_table('batch_handheld')
