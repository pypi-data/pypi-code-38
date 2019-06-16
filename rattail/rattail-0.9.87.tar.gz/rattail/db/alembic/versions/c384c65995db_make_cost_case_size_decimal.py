# -*- coding: utf-8 -*-
"""make cost.case_size decimal

Revision ID: c384c65995db
Revises: 8c17754a6bbf
Create Date: 2016-11-11 19:20:25.017965

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = 'c384c65995db'
down_revision = u'8c17754a6bbf'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


batch_id_seq = sa.Sequence('batch_id_seq')


def upgrade():

    # product_cost
    op.alter_column('product_cost', 'case_size', type_=sa.Numeric(precision=9, scale=4))


def downgrade():

    # product_cost
    op.alter_column('product_cost', 'case_size', type_=sa.Integer())
