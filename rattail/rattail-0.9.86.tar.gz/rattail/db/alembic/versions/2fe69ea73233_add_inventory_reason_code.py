# -*- coding: utf-8 -*-
"""add inventory reason code

Revision ID: 2fe69ea73233
Revises: 5b88c82dbd8d
Create Date: 2017-07-11 21:30:01.552398

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '2fe69ea73233'
down_revision = u'5b88c82dbd8d'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_inventory
    op.add_column('batch_inventory', sa.Column('reason_code', sa.String(length=50), nullable=True))


def downgrade():

    # batch_inventory
    op.drop_column('batch_inventory', 'reason_code')
