# -*- coding: utf-8; -*-
"""add pricing_batch.filename

Revision ID: c02430f167c2
Revises: f7dc4e92752c
Create Date: 2018-12-17 22:05:06.558470

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'c02430f167c2'
down_revision = 'f7dc4e92752c'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_pricing
    op.add_column('batch_pricing', sa.Column('input_filename', sa.String(length=255), nullable=True))


def downgrade():

    # batch_pricing
    op.drop_column('batch_pricing', 'input_filename')
