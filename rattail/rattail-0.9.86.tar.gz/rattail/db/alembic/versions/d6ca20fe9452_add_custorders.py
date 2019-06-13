# -*- coding: utf-8 -*-
"""add custorders

Revision ID: d6ca20fe9452
Revises: 09ed5bdc99f1
Create Date: 2017-02-16 20:53:48.730360

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = 'd6ca20fe9452'
down_revision = u'09ed5bdc99f1'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # custorder
    op.create_table('custorder',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=True),
                    sa.Column('customer_uuid', sa.String(length=32), nullable=True),
                    sa.Column('person_uuid', sa.String(length=32), nullable=True),
                    sa.Column('created', sa.DateTime(), nullable=False),
                    sa.Column('status_code', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['customer_uuid'], [u'customer.uuid'], name=u'custorder_fk_customer'),
                    sa.ForeignKeyConstraint(['person_uuid'], [u'person.uuid'], name=u'custorder_fk_person'),
                    sa.PrimaryKeyConstraint('uuid')
    )

    # custorder_item
    op.create_table('custorder_item',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('order_uuid', sa.String(length=32), nullable=False),
                    sa.Column('sequence', sa.Integer(), nullable=False),
                    sa.Column('product_uuid', sa.String(length=32), nullable=True),
                    sa.Column('product_brand', sa.String(length=100), nullable=True),
                    sa.Column('product_description', sa.String(length=60), nullable=True),
                    sa.Column('product_size', sa.String(length=30), nullable=True),
                    sa.Column('product_unit_of_measure', sa.String(length=4), nullable=False),
                    sa.Column('department_number', sa.Integer(), nullable=True),
                    sa.Column('department_name', sa.String(length=30), nullable=True),
                    sa.Column('case_quantity', sa.Numeric(precision=10, scale=4), nullable=True),
                    sa.Column('cases_ordered', sa.Numeric(precision=10, scale=4), nullable=True),
                    sa.Column('units_ordered', sa.Numeric(precision=10, scale=4), nullable=True),
                    sa.Column('product_unit_cost', sa.Numeric(precision=9, scale=5), nullable=True),
                    sa.Column('unit_price', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.Column('discount_percent', sa.Numeric(precision=5, scale=3), nullable=False),
                    sa.Column('total_price', sa.Numeric(precision=8, scale=3), nullable=True),
                    sa.Column('paid_amount', sa.Numeric(precision=8, scale=3), nullable=False),
                    sa.Column('payment_transaction_number', sa.String(length=8), nullable=True),
                    sa.Column('status_code', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['order_uuid'], [u'custorder.uuid'], name=u'custorder_item_fk_order'),
                    sa.ForeignKeyConstraint(['product_uuid'], [u'product.uuid'], name=u'custorder_item_fk_product'),
                    sa.PrimaryKeyConstraint('uuid')
    )

    # custorder_item_event
    op.create_table('custorder_item_event',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('item_uuid', sa.String(length=32), nullable=False),
                    sa.Column('type_code', sa.Integer(), nullable=False),
                    sa.Column('occurred', sa.DateTime(), nullable=False),
                    sa.Column('user_uuid', sa.String(length=32), nullable=False),
                    sa.Column('note', sa.Text(), nullable=True),
                    sa.ForeignKeyConstraint(['item_uuid'], [u'custorder_item.uuid'], name=u'custorder_item_event_fk_item'),
                    sa.ForeignKeyConstraint(['user_uuid'], [u'user.uuid'], name=u'custorder_item_event_fk_user'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # custorder*
    op.drop_table('custorder_item_event')
    op.drop_table('custorder_item')
    op.drop_table('custorder')
