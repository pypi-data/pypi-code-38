# -*- coding: utf-8 -*-
"""inventory from handheld batches

Revision ID: a5a7358ed27f
Revises: 3e79dd89fe12
Create Date: 2017-06-21 15:21:03.737309

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = 'a5a7358ed27f'
down_revision = u'3e79dd89fe12'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql
from rattail.core import get_uuid


def upgrade():

    # batch_inventory_handheld
    batch_inventory_handheld = op.create_table('batch_inventory_handheld',
                                               sa.Column('uuid', sa.String(length=32), nullable=False),
                                               sa.Column('batch_uuid', sa.String(length=32), nullable=False),
                                               sa.Column('ordinal', sa.Integer(), nullable=False),
                                               sa.Column('handheld_uuid', sa.String(length=32), nullable=False),
                                               sa.ForeignKeyConstraint(['batch_uuid'], [u'batch_inventory.uuid'], name=u'batch_inventory_handheld_fk_batch'),
                                               sa.ForeignKeyConstraint(['handheld_uuid'], [u'batch_handheld.uuid'], name=u'batch_inventory_handheld_fk_handheld'),
                                               sa.PrimaryKeyConstraint('uuid')
    )

    # migrate data from inventory batch header, to new association table
    batch_inventory = sa.sql.table('batch_inventory',
                                   sa.sql.column('uuid'),
                                   sa.sql.column('handheld_batch_uuid'))
    cursor = op.get_bind().execute(batch_inventory.select())
    for row in cursor.fetchall():
        if row['handheld_batch_uuid']:
            op.get_bind().execute(batch_inventory_handheld.insert().values({
                'uuid': get_uuid(),
                'batch_uuid': row['uuid'],
                'handheld_uuid': row['handheld_batch_uuid'],
                'ordinal': 1,
            }))


def downgrade():

    # batch_inventory_handheld
    op.drop_table('batch_inventory_handheld')
