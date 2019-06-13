# -*- coding: utf-8; -*-
"""update brand version

Revision ID: 9f1d111fa775
Revises: de4ebbf5bbb3
Create Date: 2018-01-26 14:46:18.840423

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '9f1d111fa775'
down_revision = u'de4ebbf5bbb3'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # brand
    op.add_column('brand_version', sa.Column('confirmed', sa.Boolean(), autoincrement=False, nullable=True))


def downgrade():

    # brand
    op.drop_column('brand_version', 'confirmed')
