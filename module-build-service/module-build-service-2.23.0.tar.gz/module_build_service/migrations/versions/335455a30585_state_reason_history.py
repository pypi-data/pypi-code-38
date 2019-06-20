"""state reason history

Revision ID: 335455a30585
Revises: 474697622859
Create Date: 2017-02-10 11:38:55.249234

"""

# revision identifiers, used by Alembic.
revision = '335455a30585'
down_revision = '474697622859'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'module_builds_trace',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('module_id', sa.Integer(), sa.ForeignKey('module_builds.id'), nullable=False),
        sa.Column('state_time', sa.DateTime(), nullable=False),
        sa.Column('state', sa.Integer(), nullable=True),
        sa.Column('state_reason', sa.String(), nullable=True)
    )

    op.create_table(
        'component_builds_trace',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('component_id', sa.Integer(), sa.ForeignKey('component_builds.id'), nullable=False),
        sa.Column('state_time', sa.DateTime(), nullable=False),
        sa.Column('state', sa.Integer(), nullable=True),
        sa.Column('state_reason', sa.String(), nullable=True),
        sa.Column('task_id', sa.Integer(), nullable=True),
    )


def downgrade():
    op.drop_table('module_builds_trace')
    op.drop_table('component_builds_trace')
