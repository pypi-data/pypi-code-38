# -*- coding: utf-8; -*-
"""add category, family for product batch

Revision ID: 90d5e8185d44
Revises: e1685bf9f1ad
Create Date: 2019-04-23 22:41:30.384291

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '90d5e8185d44'
down_revision = 'e1685bf9f1ad'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_product_row
    op.add_column('batch_product_row', sa.Column('category_uuid', sa.String(length=32), nullable=True))
    op.add_column('batch_product_row', sa.Column('family_uuid', sa.String(length=32), nullable=True))
    op.add_column('batch_product_row', sa.Column('reportcode_uuid', sa.String(length=32), nullable=True))
    op.create_foreign_key('batch_product_row_fk_category', 'batch_product_row', 'category', ['category_uuid'], ['uuid'])
    op.create_foreign_key('batch_product_row_fk_family', 'batch_product_row', 'family', ['family_uuid'], ['uuid'])
    op.create_foreign_key('batch_product_row_fk_reportcode', 'batch_product_row', 'report_code', ['reportcode_uuid'], ['uuid'])


def downgrade():

    # batch_product_row
    op.drop_constraint('batch_product_row_fk_reportcode', 'batch_product_row', type_='foreignkey')
    op.drop_constraint('batch_product_row_fk_family', 'batch_product_row', type_='foreignkey')
    op.drop_constraint('batch_product_row_fk_category', 'batch_product_row', type_='foreignkey')
    op.drop_column('batch_product_row', 'reportcode_uuid')
    op.drop_column('batch_product_row', 'family_uuid')
    op.drop_column('batch_product_row', 'category_uuid')
