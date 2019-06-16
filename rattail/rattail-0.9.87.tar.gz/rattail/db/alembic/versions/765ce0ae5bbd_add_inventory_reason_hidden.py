# -*- coding: utf-8 -*-
"""add inventory_reason.hidden

Revision ID: 765ce0ae5bbd
Revises: a33583135905
Create Date: 2018-06-01 12:52:46.968644

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '765ce0ae5bbd'
down_revision = u'a33583135905'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # invadjust_reason
    op.add_column('invadjust_reason', sa.Column('hidden', sa.Boolean(), nullable=True))


def downgrade():

    # invadjust_reason
    op.drop_column('invadjust_reason', 'hidden')
