# -*- coding: utf-8 -*-
"""make invoice quantities decimal

Revision ID: 3ef0fbcfb42e
Revises: 2dd756a44a16
Create Date: 2015-02-23 20:02:57.049418

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '3ef0fbcfb42e'
down_revision = u'2dd756a44a16'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():
    op.alter_column('vendor_invoice_row', 'ordered_cases', type_=sa.Numeric(precision=9, scale=4))
    op.alter_column('vendor_invoice_row', 'ordered_units', type_=sa.Numeric(precision=9, scale=4))
    op.alter_column('vendor_invoice_row', 'shipped_cases', type_=sa.Numeric(precision=9, scale=4))
    op.alter_column('vendor_invoice_row', 'shipped_units', type_=sa.Numeric(precision=9, scale=4))


def downgrade():
    op.alter_column('vendor_invoice_row', 'ordered_cases', type_=sa.Integer())
    op.alter_column('vendor_invoice_row', 'ordered_units', type_=sa.Integer())
    op.alter_column('vendor_invoice_row', 'shipped_cases', type_=sa.Integer())
    op.alter_column('vendor_invoice_row', 'shipped_units', type_=sa.Integer())
