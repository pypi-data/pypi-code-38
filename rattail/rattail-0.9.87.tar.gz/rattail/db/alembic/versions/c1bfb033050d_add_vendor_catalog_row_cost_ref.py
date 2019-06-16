# -*- coding: utf-8; -*-
"""add vendor_catalog_row.cost ref

Revision ID: c1bfb033050d
Revises: ccd32c44393f
Create Date: 2018-04-05 22:45:04.638730

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = 'c1bfb033050d'
down_revision = u'ccd32c44393f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # vendor_catalog_row
    op.add_column('vendor_catalog_row', sa.Column('cost_uuid', sa.String(length=32), nullable=True))
    op.create_foreign_key(u'vendor_catalog_row_fk_cost', 'vendor_catalog_row', 'product_cost', ['cost_uuid'], ['uuid'])


def downgrade():

    # vendor_catalog_row
    op.drop_constraint(u'vendor_catalog_row_fk_cost', 'vendor_catalog_row', type_='foreignkey')
    op.drop_column('vendor_catalog_row', 'cost_uuid')
