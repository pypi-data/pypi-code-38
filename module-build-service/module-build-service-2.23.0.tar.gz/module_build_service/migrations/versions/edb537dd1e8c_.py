"""Add cg_build_koji_tag

Revision ID: edb537dd1e8c
Revises: c11a3cfec2a9
Create Date: 2017-09-22 13:50:41.433144

"""

# revision identifiers, used by Alembic.
revision = 'edb537dd1e8c'
down_revision = 'c11a3cfec2a9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('module_builds', sa.Column('cg_build_koji_tag', sa.String(), nullable=True))


def downgrade():
    op.drop_column('module_builds', 'cg_build_koji_tag')
