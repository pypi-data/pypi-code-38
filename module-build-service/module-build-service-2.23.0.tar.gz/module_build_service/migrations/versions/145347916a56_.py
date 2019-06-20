"""Drops the release column, adds stream column

Revision ID: 145347916a56
Revises: 229f6f273a56
Create Date: 2016-11-10 15:53:21.798038

"""

# revision identifiers, used by Alembic.
revision = '145347916a56'
down_revision = '229f6f273a56'

from alembic import op
import sqlalchemy as sa


def upgrade():
    with op.batch_alter_table('module_builds', schema=None) as batch_op:
        batch_op.add_column(sa.Column('stream', sa.String(), nullable=False))
        batch_op.drop_column('release')

def downgrade():
    with op.batch_alter_table('module_builds', schema=None) as batch_op:
        batch_op.add_column(sa.Column('release', sa.VARCHAR(), nullable=False))
        batch_op.drop_column('stream')
