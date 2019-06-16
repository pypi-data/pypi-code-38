# -*- coding: utf-8; -*-
"""add purchase_batch.truck_dump_status

Revision ID: 03be1584f923
Revises: 40a4855cb22d
Create Date: 2019-03-01 10:50:37.053705

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '03be1584f923'
down_revision = '40a4855cb22d'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types


BATCH_STATUS_TRUCKDUMP_UNCLAIMED        = 3
BATCH_STATUS_TRUCKDUMP_CLAIMED          = 4

ROW_STATUS_TRUCKDUMP_UNCLAIMED          = 7
ROW_STATUS_TRUCKDUMP_CLAIMED            = 8
ROW_STATUS_TRUCKDUMP_OVERCLAIMED        = 9
ROW_STATUS_TRUCKDUMP_PARTCLAIMED        = 11


def upgrade():

    # purchase_batch
    op.add_column('purchase_batch', sa.Column('truck_dump_status', sa.Integer(), nullable=True))
    batch = sa.sql.table('purchase_batch',
                         sa.sql.column('status_code'),
                         sa.sql.column('truck_dump_status'))
    op.execute(batch.update()\
               .where(batch.c.status_code == BATCH_STATUS_TRUCKDUMP_UNCLAIMED)\
               .values({'truck_dump_status': BATCH_STATUS_TRUCKDUMP_UNCLAIMED}))
    op.execute(batch.update()\
               .where(batch.c.status_code == BATCH_STATUS_TRUCKDUMP_CLAIMED)\
               .values({'truck_dump_status': BATCH_STATUS_TRUCKDUMP_CLAIMED}))

    # purchase_batch_row
    op.add_column('purchase_batch_row', sa.Column('truck_dump_status', sa.Integer(), nullable=True))
    row = sa.sql.table('purchase_batch_row',
                       sa.sql.column('status_code'),
                       sa.sql.column('truck_dump_status'))
    op.execute(row.update()\
               .where(row.c.status_code == ROW_STATUS_TRUCKDUMP_UNCLAIMED)\
               .values({'truck_dump_status': ROW_STATUS_TRUCKDUMP_UNCLAIMED}))
    op.execute(row.update()\
               .where(row.c.status_code == ROW_STATUS_TRUCKDUMP_CLAIMED)\
               .values({'truck_dump_status': ROW_STATUS_TRUCKDUMP_CLAIMED}))
    op.execute(row.update()\
               .where(row.c.status_code == ROW_STATUS_TRUCKDUMP_OVERCLAIMED)\
               .values({'truck_dump_status': ROW_STATUS_TRUCKDUMP_OVERCLAIMED}))
    op.execute(row.update()\
               .where(row.c.status_code == ROW_STATUS_TRUCKDUMP_PARTCLAIMED)\
               .values({'truck_dump_status': ROW_STATUS_TRUCKDUMP_PARTCLAIMED}))


def downgrade():

    # purchase_batch_row
    op.drop_column('purchase_batch_row', 'truck_dump_status')

    # purchase_batch
    op.drop_column('purchase_batch', 'truck_dump_status')
