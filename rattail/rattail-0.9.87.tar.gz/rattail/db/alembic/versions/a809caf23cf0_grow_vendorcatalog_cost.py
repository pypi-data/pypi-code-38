# -*- coding: utf-8 -*-
"""grow vendorcatalog.cost

Revision ID: a809caf23cf0
Revises: 9de6ffc1d2af
Create Date: 2017-12-21 20:11:02.812699

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'a809caf23cf0'
down_revision = u'9de6ffc1d2af'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # vendor_catalog_row
    op.alter_column('vendor_catalog_row', 'case_cost', type_=sa.Numeric(precision=10, scale=5))
    op.alter_column('vendor_catalog_row', 'unit_cost', type_=sa.Numeric(precision=10, scale=5))
    op.alter_column('vendor_catalog_row', 'old_case_cost', type_=sa.Numeric(precision=10, scale=5))
    op.alter_column('vendor_catalog_row', 'old_unit_cost', type_=sa.Numeric(precision=10, scale=5))
    op.alter_column('vendor_catalog_row', 'case_cost_diff', type_=sa.Numeric(precision=10, scale=5))
    op.alter_column('vendor_catalog_row', 'unit_cost_diff', type_=sa.Numeric(precision=10, scale=5))


def downgrade():

    # vendor_catalog_row
    op.alter_column('vendor_catalog_row', 'unit_cost_diff', type_=sa.Numeric(precision=9, scale=5))
    op.alter_column('vendor_catalog_row', 'case_cost_diff', type_=sa.Numeric(precision=9, scale=5))
    op.alter_column('vendor_catalog_row', 'old_unit_cost', type_=sa.Numeric(precision=9, scale=5))
    op.alter_column('vendor_catalog_row', 'old_case_cost', type_=sa.Numeric(precision=9, scale=5))
    op.alter_column('vendor_catalog_row', 'unit_cost', type_=sa.Numeric(precision=9, scale=5))
    op.alter_column('vendor_catalog_row', 'case_cost', type_=sa.Numeric(precision=9, scale=5))
