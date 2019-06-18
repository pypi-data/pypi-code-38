"""Add module_arches and module_builds_to_arches tables.

Revision ID: bf861b6af29a
Revises: 65ad4fcdbce6
Create Date: 2019-06-03 13:33:40.540567

"""

# revision identifiers, used by Alembic.
revision = 'bf861b6af29a'
down_revision = '65ad4fcdbce6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('module_arches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    op.create_table('module_builds_to_arches',
        sa.Column('module_build_id', sa.Integer(), nullable=False),
        sa.Column('module_arch_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['module_arch_id'], ['module_arches.id'], ),
        sa.ForeignKeyConstraint(['module_build_id'], ['module_builds.id'], ),
        sa.UniqueConstraint('module_build_id', 'module_arch_id', name='unique_module_to_arch')
    )


def downgrade():
    op.drop_table('module_builds_to_arches')
    op.drop_table('module_arches')
