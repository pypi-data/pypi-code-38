"""Add component_builds.weight

Revision ID: f5b1c5203cce
Revises: 524c3b1c683c
Create Date: 2017-11-08 17:18:27.401546

"""

# revision identifiers, used by Alembic.
revision = 'f5b1c5203cce'
down_revision = '524c3b1c683c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('component_builds', sa.Column('weight', sa.Float(), nullable=True))


def downgrade():
    op.drop_column('component_builds', 'weight')
