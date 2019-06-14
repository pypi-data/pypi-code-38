"""Add koji_task_id

Revision ID: e2163db7b15d
Revises: b75ad2afc207
Create Date: 2017-12-13 08:42:05.900658

"""

# revision identifiers, used by Alembic.
revision = 'e2163db7b15d'
down_revision = 'b75ad2afc207'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('composes', sa.Column('koji_task_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_composes_koji_task_id'), 'composes', ['koji_task_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_composes_koji_task_id'), table_name='composes')
    op.drop_column('composes', 'koji_task_id')
