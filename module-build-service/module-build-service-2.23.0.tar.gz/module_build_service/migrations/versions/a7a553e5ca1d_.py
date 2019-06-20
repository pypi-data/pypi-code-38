"""Initial database migration script that creates the database tables

Revision ID: a7a553e5ca1d
Revises: None
Create Date: 2016-08-01 16:48:23.979017

"""

# revision identifiers, used by Alembic.
revision = 'a7a553e5ca1d'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('module_builds',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('version', sa.String(), nullable=False),
    sa.Column('release', sa.String(), nullable=False),
    sa.Column('state', sa.Integer(), nullable=False),
    sa.Column('modulemd', sa.String(), nullable=False),
    sa.Column('koji_tag', sa.String(), nullable=True),
    sa.Column('scmurl', sa.String(), nullable=True),
    sa.Column('batch', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('component_builds',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('package', sa.String(), nullable=False),
    sa.Column('scmurl', sa.String(), nullable=False),
    sa.Column('format', sa.String(), nullable=False),
    sa.Column('task_id', sa.Integer(), nullable=True),
    sa.Column('state', sa.Integer(), nullable=True),
    sa.Column('nvr', sa.String(), nullable=True),
    sa.Column('batch', sa.Integer(), nullable=True),
    sa.Column('module_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['module_id'], ['module_builds.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('component_builds')
    op.drop_table('module_builds')
