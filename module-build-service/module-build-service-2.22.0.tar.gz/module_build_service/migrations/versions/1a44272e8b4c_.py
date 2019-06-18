"""Adds the owner, time_completed, time_modified, and time_submitted columns to the module_builds table

Revision ID: 1a44272e8b4c
Revises: a7a553e5ca1d
Create Date: 2016-08-17 17:00:31.126429

"""

# revision identifiers, used by Alembic.
revision = '1a44272e8b4c'
down_revision = 'a7a553e5ca1d'

from alembic import op
import sqlalchemy as sa
from datetime import datetime

epoch = datetime.utcfromtimestamp(0).strftime('%Y-%m-%d %H:%M:%S')


def upgrade():
    op.add_column('module_builds', sa.Column('owner', sa.String(), server_default='Unknown User', nullable=False))
    op.add_column('module_builds', sa.Column('time_completed', sa.DateTime(), nullable=True, server_default=epoch))
    op.add_column('module_builds', sa.Column('time_modified', sa.DateTime(), nullable=True, server_default=epoch))
    op.add_column('module_builds', sa.Column('time_submitted', sa.DateTime(), nullable=False, server_default=epoch))

    # Remove migration-only defaults. Using batch_alter_table() recreates the table instead of using ALTER COLUMN
    # on simplistic DB engines. Thanks SQLite!
    with op.batch_alter_table('module_builds') as b:
        b.alter_column('owner', server_default=None)
        b.alter_column('time_completed', server_default=None)
        b.alter_column('time_modified', server_default=None)
        b.alter_column('time_submitted', server_default=None)


def downgrade():
    # Thanks again!
    with op.batch_alter_table('module_builds') as b:
        b.drop_column('time_submitted')
        b.drop_column('time_modified')
        b.drop_column('time_completed')
        b.drop_column('owner')
