# -*- coding: utf-8 -*-
"""enlarge product_cost.code

Revision ID: 571c070b7080
Revises: f950be5601a
Create Date: 2015-02-11 19:11:36.664874

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '571c070b7080'
down_revision = u'f950be5601a'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():
    op.alter_column('product_cost', 'code', type_=sa.String(length=20))
    op.alter_column('product_cost_version', 'code', type_=sa.String(length=20))


def downgrade():
    op.alter_column('product_cost_version', 'code', type_=sa.String(length=15))
    op.alter_column('product_cost', 'code', type_=sa.String(length=15))
