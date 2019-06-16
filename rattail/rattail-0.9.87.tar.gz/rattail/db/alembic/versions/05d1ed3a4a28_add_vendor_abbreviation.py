# -*- coding: utf-8; -*-
"""add vendor.abbreviation

Revision ID: 05d1ed3a4a28
Revises: 765ce0ae5bbd
Create Date: 2018-06-01 14:28:56.127658

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '05d1ed3a4a28'
down_revision = '765ce0ae5bbd'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # vendor
    op.add_column('vendor', sa.Column('abbreviation', sa.String(length=20), nullable=True))
    op.add_column('vendor_version', sa.Column('abbreviation', sa.String(length=20), autoincrement=False, nullable=True))


def downgrade():

    # vendor
    op.drop_column('vendor_version', 'abbreviation')
    op.drop_column('vendor', 'abbreviation')
