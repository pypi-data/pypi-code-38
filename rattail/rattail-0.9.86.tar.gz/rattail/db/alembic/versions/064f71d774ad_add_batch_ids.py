# -*- coding: utf-8 -*-
"""add batch ids

Revision ID: 064f71d774ad
Revises: 4137e9938122
Create Date: 2016-08-16 19:21:58.543558

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '064f71d774ad'
down_revision = u'4137e9938122'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


batch_id_seq = sa.Sequence('batch_id_seq')


def upgrade():
    from sqlalchemy.schema import CreateSequence

    # batch_id_seq
    op.execute(CreateSequence(batch_id_seq))

    # vendor_catalog
    op.add_column('vendor_catalog', sa.Column('id', sa.Integer(), batch_id_seq, nullable=True))
    vendor_catalog = sa.sql.table('vendor_catalog', sa.sql.column('id'))
    op.execute(vendor_catalog.update().values({'id': batch_id_seq.next_value()}))
    op.alter_column('vendor_catalog', 'id', nullable=False)

    # vendor_invoice
    op.add_column('vendor_invoice', sa.Column('id', sa.Integer(), batch_id_seq, nullable=True))
    vendor_invoice = sa.sql.table('vendor_invoice', sa.sql.column('id'))
    op.execute(vendor_invoice.update().values({'id': batch_id_seq.next_value()}))
    op.alter_column('vendor_invoice', 'id', nullable=False)


def downgrade():

    # vendor_invoice
    op.drop_column('vendor_invoice', 'id')

    # vendor_catalog
    op.drop_column('vendor_catalog', 'id')
