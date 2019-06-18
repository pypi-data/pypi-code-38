"""Add optional columns for copr

Revision ID: 474697622859
Revises: a1fc0736bca8
Create Date: 2017-02-21 11:18:22.304038

"""

# revision identifiers, used by Alembic.
revision = '474697622859'
down_revision = 'a1fc0736bca8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('module_builds', sa.Column('copr_owner', sa.String(), nullable=True))
    op.add_column('module_builds', sa.Column('copr_project', sa.String(), nullable=True))


def downgrade():
    op.drop_column('module_builds', 'copr_owner')
    op.drop_column('module_builds', 'copr_project')
