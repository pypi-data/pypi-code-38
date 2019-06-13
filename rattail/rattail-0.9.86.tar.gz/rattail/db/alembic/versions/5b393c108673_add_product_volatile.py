# -*- coding: utf-8; -*-
"""add product_volatile

Revision ID: 5b393c108673
Revises: 6118198dc4db
Create Date: 2019-03-08 13:14:11.645892

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '5b393c108673'
down_revision = '6118198dc4db'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # product_volatile
    op.create_table('product_volatile',
                    sa.Column('uuid', sa.String(length=32), nullable=False),
                    sa.Column('product_uuid', sa.String(length=32), nullable=False),
                    sa.Column('true_cost', sa.Numeric(precision=9, scale=5), nullable=True),
                    sa.Column('true_margin', sa.Numeric(precision=8, scale=5), nullable=True),
                    sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'], name='product_volatile_fk_product'),
                    sa.PrimaryKeyConstraint('uuid')
    )


def downgrade():

    # product_volatile
    op.drop_table('product_volatile')
