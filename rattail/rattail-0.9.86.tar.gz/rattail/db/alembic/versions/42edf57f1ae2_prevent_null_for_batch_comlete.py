# -*- coding: utf-8 -*-
"""prevent null for batch.comlete

Revision ID: 42edf57f1ae2
Revises: 391fac830cb1
Create Date: 2018-09-22 18:58:20.563028

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '42edf57f1ae2'
down_revision = '391fac830cb1'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch_handheld
    batch = sa.sql.table('batch_handheld', sa.sql.column('complete'))
    op.execute(batch.update()\
               .where(batch.c.complete == None)\
               .values({'complete': False}))
    op.alter_column('batch_handheld', 'complete', nullable=False)

    # batch_importer
    batch = sa.sql.table('batch_importer', sa.sql.column('complete'))
    op.execute(batch.update()\
               .where(batch.c.complete == None)\
               .values({'complete': False}))
    op.alter_column('batch_importer', 'complete', nullable=False)

    # batch_inventory
    batch = sa.sql.table('batch_inventory', sa.sql.column('complete'))
    op.execute(batch.update()\
               .where(batch.c.complete == None)\
               .values({'complete': False}))
    op.alter_column('batch_inventory', 'complete', nullable=False)

    # batch_pricing
    batch = sa.sql.table('batch_pricing', sa.sql.column('complete'))
    op.execute(batch.update()\
               .where(batch.c.complete == None)\
               .values({'complete': False}))
    op.alter_column('batch_pricing', 'complete', nullable=False)

    # label_batch
    batch = sa.sql.table('label_batch', sa.sql.column('complete'))
    op.execute(batch.update()\
               .where(batch.c.complete == None)\
               .values({'complete': False}))
    op.alter_column('label_batch', 'complete', nullable=False)

    # purchase_batch
    batch = sa.sql.table('purchase_batch', sa.sql.column('complete'))
    op.execute(batch.update()\
               .where(batch.c.complete == None)\
               .values({'complete': False}))
    op.alter_column('purchase_batch', 'complete', nullable=False)

    # vendor_catalog
    batch = sa.sql.table('vendor_catalog', sa.sql.column('complete'))
    op.execute(batch.update()\
               .where(batch.c.complete == None)\
               .values({'complete': False}))
    op.alter_column('vendor_catalog', 'complete', nullable=False)

    # vendor_invoice
    batch = sa.sql.table('vendor_invoice', sa.sql.column('complete'))
    op.execute(batch.update()\
               .where(batch.c.complete == None)\
               .values({'complete': False}))
    op.alter_column('vendor_invoice', 'complete', nullable=False)


def downgrade():

    # downgrade is simpler, we just need to allow null again
    op.alter_column('vendor_invoice', 'complete', nullable=True)
    op.alter_column('vendor_catalog', 'complete', nullable=True)
    op.alter_column('purchase_batch', 'complete', nullable=True)
    op.alter_column('label_batch', 'complete', nullable=True)
    op.alter_column('batch_pricing', 'complete', nullable=True)
    op.alter_column('batch_inventory', 'complete', nullable=True)
    op.alter_column('batch_importer', 'complete', nullable=True)
    op.alter_column('batch_handheld', 'complete', nullable=True)
