# -*- coding: utf-8 -*-
"""add label/handheld batch(es) tie

Revision ID: 3e79dd89fe12
Revises: 043d4bafc0be
Create Date: 2017-06-21 14:19:14.308813

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '3e79dd89fe12'
down_revision = u'043d4bafc0be'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql
from rattail.core import get_uuid


def upgrade():

    # label_batch_handheld
    label_batch_handheld = op.create_table('label_batch_handheld',
                                           sa.Column('uuid', sa.String(length=32), nullable=False),
                                           sa.Column('batch_uuid', sa.String(length=32), nullable=False),
                                           sa.Column('handheld_uuid', sa.String(length=32), nullable=False),
                                           sa.Column('ordinal', sa.Integer(), nullable=False),
                                           sa.ForeignKeyConstraint(['batch_uuid'], [u'label_batch.uuid'], name=u'label_batch_handheld_fk_batch'),
                                           sa.ForeignKeyConstraint(['handheld_uuid'], [u'batch_handheld.uuid'], name=u'label_batch_handheld_fk_handheld'),
                                           sa.PrimaryKeyConstraint('uuid')
    )

    # migrate data from label batch header, to new association table
    label_batch = sa.sql.table('label_batch',
                               sa.sql.column('uuid'),
                               sa.sql.column('handheld_batch_uuid'))
    cursor = op.get_bind().execute(label_batch.select())
    for row in cursor.fetchall():
        if row['handheld_batch_uuid']:
            op.get_bind().execute(label_batch_handheld.insert().values({
                'uuid': get_uuid(),
                'batch_uuid': row['uuid'],
                'handheld_uuid': row['handheld_batch_uuid'],
                'ordinal': 1,
            }))


def downgrade():

    # label_batch_handheld
    op.drop_table('label_batch_handheld')
