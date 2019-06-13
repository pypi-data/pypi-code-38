# -*- coding: utf-8; -*-
"""grow label_profile.code

Revision ID: a7b7246e48e2
Revises: 95a66a59d420
Create Date: 2018-12-18 19:02:13.497715

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'a7b7246e48e2'
down_revision = '95a66a59d420'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # label_profile
    op.alter_column('label_profile', 'code', type_=sa.String(length=30))

    # label_batch
    op.alter_column('label_batch_row', 'label_code', type_=sa.String(length=30))


def downgrade():

    # label_batch
    op.alter_column('label_batch_row', 'label_code', type_=sa.String(length=3))

    # label_profile
    op.alter_column('label_profile', 'code', type_=sa.String(length=3))
