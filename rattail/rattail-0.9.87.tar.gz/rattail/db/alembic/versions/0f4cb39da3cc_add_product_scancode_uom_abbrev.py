# -*- coding: utf-8 -*-
"""add product scancode, uom_abbrev

Revision ID: 0f4cb39da3cc
Revises: 193c2dcdd14d
Create Date: 2016-12-15 13:48:53.182996

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '0f4cb39da3cc'
down_revision = u'193c2dcdd14d'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


batch_id_seq = sa.Sequence('batch_id_seq')


def upgrade():

    # product
    op.add_column('product', sa.Column('scancode', sa.String(length=14), nullable=True))
    op.add_column('product', sa.Column('uom_abbreviation', sa.String(length=4), nullable=True))


def downgrade():

    # product
    op.drop_column('product', 'uom_abbreviation')
    op.drop_column('product', 'scancode')
