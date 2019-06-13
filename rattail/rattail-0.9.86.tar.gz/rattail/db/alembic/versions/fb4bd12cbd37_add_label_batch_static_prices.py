# -*- coding: utf-8 -*-
"""add label_batch.static_prices

Revision ID: fb4bd12cbd37
Revises: 6a02ca0279c9
Create Date: 2017-12-02 14:55:42.219938

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'fb4bd12cbd37'
down_revision = u'6a02ca0279c9'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # label_batch
    op.add_column('label_batch', sa.Column('static_prices', sa.Boolean(), nullable=True))


def downgrade():

    # label_batch
    op.drop_column('label_batch', 'static_prices')
