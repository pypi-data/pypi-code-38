# -*- coding: utf-8; -*-
"""add label_batch.label_profile

Revision ID: 95a66a59d420
Revises: bd7acb7028da
Create Date: 2018-12-18 18:20:10.722491

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '95a66a59d420'
down_revision = 'bd7acb7028da'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types



def upgrade():

    # label_batch
    op.add_column('label_batch', sa.Column('label_profile_uuid', sa.String(length=32), nullable=True))
    op.create_foreign_key('label_batch_fk_label_profile', 'label_batch', 'label_profile', ['label_profile_uuid'], ['uuid'])


def downgrade():

    # label_batch
    op.drop_constraint('label_batch_fk_label_profile', 'label_batch', type_='foreignkey')
    op.drop_column('label_batch', 'label_profile_uuid')
