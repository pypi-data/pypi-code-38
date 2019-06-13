# -*- coding: utf-8; -*-
"""add product.suggested_price

Revision ID: 11a9145414a9
Revises: c2085638f487
Create Date: 2018-11-08 08:36:27.171039

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '11a9145414a9'
down_revision = 'c2085638f487'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # product
    op.add_column('product', sa.Column('suggested_price_uuid', sa.String(length=32), nullable=True))
    op.create_foreign_key('product_fk_suggested_price', 'product', 'product_price', ['suggested_price_uuid'], ['uuid'], use_alter=True)
    op.add_column('product_version', sa.Column('suggested_price_uuid', sa.String(length=32), autoincrement=False, nullable=True))


def downgrade():

    # product
    op.drop_column('product_version', 'suggested_price_uuid')
    op.drop_constraint('product_fk_suggested_price', 'product', type_='foreignkey')
    op.drop_column('product', 'suggested_price_uuid')
