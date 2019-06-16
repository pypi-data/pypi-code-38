# -*- coding: utf-8 -*-
"""add purchase_batch.invoice_file

Revision ID: 92a49edc45c3
Revises: 6551a4d9ff25
Create Date: 2018-05-16 13:46:31.940108

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '92a49edc45c3'
down_revision = u'6551a4d9ff25'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # purchase_batch
    op.add_column('purchase_batch', sa.Column('invoice_file', sa.String(length=255), nullable=True))
    op.add_column('purchase_batch', sa.Column('invoice_parser_key', sa.String(length=100), nullable=True))


def downgrade():

    # purchase_batch
    op.drop_column('purchase_batch', 'invoice_parser_key')
    op.drop_column('purchase_batch', 'invoice_file')
