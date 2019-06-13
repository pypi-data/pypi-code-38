# -*- coding: utf-8 -*-
"""grow inventory.total_cost

Revision ID: eb4e965ce771
Revises: 539c2df56562
Create Date: 2017-09-29 12:01:22.445027

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'eb4e965ce771'
down_revision = u'539c2df56562'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # batch_inventory
    op.alter_column('batch_inventory', 'total_cost', type_=sa.Numeric(precision=12, scale=5))


def downgrade():

    # batch_inventory
    op.alter_column('batch_inventory', 'total_cost', type_=sa.Numeric(precision=9, scale=5))
