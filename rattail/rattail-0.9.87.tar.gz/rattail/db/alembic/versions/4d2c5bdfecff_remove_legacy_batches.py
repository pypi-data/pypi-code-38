# -*- coding: utf-8 -*-
"""remove legacy batches

Revision ID: 4d2c5bdfecff
Revises: ea9718f6e6c6
Create Date: 2017-05-13 15:20:08.784955

"""

from __future__ import unicode_literals, absolute_import

# revision identifiers, used by Alembic.
revision = '4d2c5bdfecff'
down_revision = 'ea9718f6e6c6'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import rattail.db.types
from sqlalchemy.dialects import postgresql


permission = sa.sql.table('permission', sa.sql.column('permission'))


def rename_perm(oldname, newname):
    op.execute(permission.update().where(permission.c.permission == oldname).values({'permission': newname}))


def upgrade():
    rename_perm('batches.create', 'products.make_batch')

    # batch*
    op.drop_table('batch_column')
    op.drop_table('batch')


def downgrade():
    rename_perm('products.make_batch', 'batches.create')

    # batch
    op.create_table('batch',
                    sa.Column('uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
                    sa.Column('provider', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
                    sa.Column('id', sa.VARCHAR(length=8), autoincrement=False, nullable=True),
                    sa.Column('source', sa.VARCHAR(length=6), autoincrement=False, nullable=True),
                    sa.Column('destination', sa.VARCHAR(length=6), autoincrement=False, nullable=True),
                    sa.Column('action_type', sa.VARCHAR(length=6), autoincrement=False, nullable=True),
                    sa.Column('description', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
                    sa.Column('rowcount', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.Column('executed', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('purge', sa.DATE(), autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('uuid', name=u'batches_pkey')
    )

    # batch_column
    op.create_table('batch_column',
                    sa.Column('uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
                    sa.Column('batch_uuid', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
                    sa.Column('ordinal', sa.INTEGER(), autoincrement=False, nullable=False),
                    sa.Column('name', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
                    sa.Column('display_name', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
                    sa.Column('sil_name', sa.VARCHAR(length=10), autoincrement=False, nullable=True),
                    sa.Column('data_type', sa.VARCHAR(length=15), autoincrement=False, nullable=True),
                    sa.Column('description', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
                    sa.Column('visible', sa.BOOLEAN(), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['batch_uuid'], [u'batch.uuid'], name=u'batch_column_fk_batch'),
                    sa.PrimaryKeyConstraint('uuid', name=u'batch_columns_pkey')
    )
