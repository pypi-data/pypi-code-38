"""Add columns for module scratch builds

Revision ID: 60c6093dde9e
Revises: 526fb7d445f7
Create Date: 2019-02-01 22:06:03.916296

"""

# revision identifiers, used by Alembic.
revision = '60c6093dde9e'
down_revision = '526fb7d445f7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('module_builds', sa.Column('scratch', sa.Boolean(), nullable=True))
    op.add_column('module_builds', sa.Column('srpms', sa.String(), nullable=True))


def downgrade():
    with op.batch_alter_table('module_builds') as b:
        b.drop_column('srpms')
        b.drop_column('scratch')
