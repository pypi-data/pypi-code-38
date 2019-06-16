# -*- coding: utf-8 -*-
"""improve size fields

Revision ID: 3544687ae150
Revises: ee253b66b7b
Create Date: 2015-02-26 23:10:16.777511

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '3544687ae150'
down_revision = u'ee253b66b7b'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from rattail import enum


def upgrade():

    # product.unit_of_measure
    product = sa.sql.table('product', sa.sql.column('unit_of_measure'))
    op.execute(product.update()\
                   .where(product.c.unit_of_measure == None)\
                   .values({'unit_of_measure': enum.UNIT_OF_MEASURE_NONE}))
    product_version = sa.sql.table('product_version', sa.sql.column('unit_of_measure'))
    op.execute(product_version.update()\
                   .where(product_version.c.unit_of_measure == None)\
                   .values({'unit_of_measure': enum.UNIT_OF_MEASURE_NONE}))
    op.alter_column('product', 'unit_of_measure', nullable=False)

    # product.unit_size
    op.add_column('product', sa.Column('unit_size', sa.Numeric(precision=8, scale=3), nullable=True))
    op.add_column('product_version', sa.Column('unit_size', sa.Numeric(precision=8, scale=3), nullable=True))

    # product.weighed
    op.add_column('product', sa.Column('weighed', sa.Boolean(), nullable=True))
    product = sa.sql.table('product', sa.sql.column('weighed'))
    op.execute(product.update().values({'weighed': False}))
    op.alter_column('product', 'weighed', nullable=False)
    op.add_column('product_version', sa.Column('weighed', sa.Boolean(), nullable=True))


def downgrade():

    # product.weighed
    op.drop_column('product_version', 'weighed')
    op.drop_column('product', 'weighed')

    # product.unit_size
    op.drop_column('product_version', 'unit_size')
    op.drop_column('product', 'unit_size')

    # product.unit_of_measure
    op.alter_column('product', 'unit_of_measure', nullable=True)
