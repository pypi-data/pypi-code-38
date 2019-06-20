"""Add component_builds.build_time_only and component_builds.tagged_in_final.

Revision ID: c11a3cfec2a9
Revises: 3b17cd6dc583
Create Date: 2017-09-15 15:23:55.357689

"""

# revision identifiers, used by Alembic.
revision = 'c11a3cfec2a9'
down_revision = '3b17cd6dc583'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('component_builds', sa.Column('build_time_only', sa.Boolean(), nullable=True))
    op.add_column('component_builds', sa.Column('tagged_in_final', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column('component_builds', 'tagged_in_final')
    op.drop_column('component_builds', 'build_time_only')
