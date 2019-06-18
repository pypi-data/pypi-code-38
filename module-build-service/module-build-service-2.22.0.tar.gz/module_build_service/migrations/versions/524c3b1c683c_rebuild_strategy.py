"""Adds the rebuild strategy column

Revision ID: 524c3b1c683c
Revises: edb537dd1e8c
Create Date: 2017-11-01 15:35:37.043545

"""

# revision identifiers, used by Alembic.
revision = '524c3b1c683c'
down_revision = 'edb537dd1e8c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('module_builds', sa.Column(
        'rebuild_strategy', sa.String(), server_default='changed-and-after', nullable=False))
    # Remove migration-only defaults
    with op.batch_alter_table('module_builds') as b:
        b.alter_column('rebuild_strategy', server_default=None)


def downgrade():
    with op.batch_alter_table('module_builds') as b:
        b.drop_column('rebuild_strategy')
