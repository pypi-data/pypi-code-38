# -*- coding: utf-8; -*-
"""grow category.code

Revision ID: 391fac830cb1
Revises: be079e974a52
Create Date: 2018-08-24 12:49:29.826310

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '391fac830cb1'
down_revision = u'be079e974a52'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # category
    op.alter_column('category', 'code', type_=sa.String(length=20))


def downgrade():

    # category
    op.alter_column('category', 'code', type_=sa.String(length=8))
