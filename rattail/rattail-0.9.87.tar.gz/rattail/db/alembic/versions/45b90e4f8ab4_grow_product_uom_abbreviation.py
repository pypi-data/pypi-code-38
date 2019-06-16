# -*- coding: utf-8; -*-
"""grow product.uom_abbreviation

Revision ID: 45b90e4f8ab4
Revises: c5f39e2dec78
Create Date: 2018-12-19 13:00:48.684227

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '45b90e4f8ab4'
down_revision = u'c5f39e2dec78'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # product
    op.alter_column('product', 'uom_abbreviation', type_=sa.String(length=10))
    op.alter_column('product_version', 'uom_abbreviation', type_=sa.String(length=10))


def downgrade():

    # product
    op.alter_column('product_version', 'uom_abbreviation', type_=sa.String(length=4))
    op.alter_column('product', 'uom_abbreviation', type_=sa.String(length=4))
