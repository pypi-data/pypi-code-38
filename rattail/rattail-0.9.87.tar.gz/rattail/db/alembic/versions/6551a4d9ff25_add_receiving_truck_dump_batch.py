# -*- coding: utf-8 -*-
"""add receiving.truck_dump_batch

Revision ID: 6551a4d9ff25
Revises: c37154504ae1
Create Date: 2018-05-16 10:40:14.855471

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '6551a4d9ff25'
down_revision = u'c37154504ae1'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # purchase_batch
    op.add_column('purchase_batch', sa.Column('truck_dump_batch_uuid', sa.String(length=32), nullable=True))
    op.create_foreign_key(u'purchase_batch_fk_truck_dump_batch', 'purchase_batch', 'purchase_batch', ['truck_dump_batch_uuid'], ['uuid'], use_alter=True)


def downgrade():

    # purchase_batch
    op.drop_constraint(u'purchase_batch_fk_truck_dump_batch', 'purchase_batch', type_='foreignkey')
    op.drop_column('purchase_batch', 'truck_dump_batch_uuid')
