# -*- coding: utf-8; -*-
"""add label_batch.label_code

Revision ID: c5f39e2dec78
Revises: a7b7246e48e2
Create Date: 2018-12-18 19:04:39.624645

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'c5f39e2dec78'
down_revision = 'a7b7246e48e2'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # label_batch
    op.add_column('label_batch', sa.Column('label_code', sa.String(length=30), nullable=True))


def downgrade():

    # label_batch
    op.drop_column('label_batch', 'label_code')
