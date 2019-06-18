"""Add new_repo_task_id and tagged columns.

Revision ID: 3b17cd6dc583
Revises: 335455a30585
Create Date: 2017-04-05 16:15:13.613851

"""

# revision identifiers, used by Alembic.
revision = '3b17cd6dc583'
down_revision = '335455a30585'

from alembic import op
import sqlalchemy as sa


def upgrade():
    with op.batch_alter_table('component_builds') as b:
        b.add_column(sa.Column('tagged', sa.Boolean(), nullable=True))
    with op.batch_alter_table('module_builds') as b:
        b.add_column(sa.Column('new_repo_task_id', sa.Integer(), nullable=True))


def downgrade():
    with op.batch_alter_table('component_builds') as b:
        b.drop_column('tagged')
    with op.batch_alter_table('module_builds') as b:
        b.drop_column('new_repo_task_id')
