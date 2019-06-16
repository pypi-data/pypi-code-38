# -*- coding: utf-8; -*-
"""grow product.description

Revision ID: aa32b6e51129
Revises: 8e965902bf93
Create Date: 2017-03-23 18:18:02.286623

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'aa32b6e51129'
down_revision = u'8e965902bf93'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


def upgrade():

    # product
    op.alter_column('product', 'description', type_=sa.String(length=255))
    op.alter_column('product', 'description2', type_=sa.String(length=255))


def downgrade():

    # product
    op.alter_column('product', 'description', type_=sa.String(length=60))
    op.alter_column('product', 'description2', type_=sa.String(length=60))
