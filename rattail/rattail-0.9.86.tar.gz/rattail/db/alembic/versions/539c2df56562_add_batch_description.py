# -*- coding: utf-8; -*-
"""add batch description

Revision ID: 539c2df56562
Revises: 1f21b32fd2a7
Create Date: 2017-08-09 19:38:28.956119

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '539c2df56562'
down_revision = u'1f21b32fd2a7'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # batch*
    op.add_column('batch_handheld', sa.Column('description', sa.String(length=255), nullable=True))
    op.add_column('batch_inventory', sa.Column('description', sa.String(length=255), nullable=True))
    op.add_column('batch_pricing', sa.Column('description', sa.String(length=255), nullable=True))
    op.add_column('label_batch', sa.Column('description', sa.String(length=255), nullable=True))
    op.add_column('purchase_batch', sa.Column('description', sa.String(length=255), nullable=True))
    op.add_column('vendor_catalog', sa.Column('description', sa.String(length=255), nullable=True))
    op.add_column('vendor_invoice', sa.Column('description', sa.String(length=255), nullable=True))


def downgrade():

    # batch*
    op.drop_column('vendor_invoice', 'description')
    op.drop_column('vendor_catalog', 'description')
    op.drop_column('purchase_batch', 'description')
    op.drop_column('label_batch', 'description')
    op.drop_column('batch_pricing', 'description')
    op.drop_column('batch_inventory', 'description')
    op.drop_column('batch_handheld', 'description')
