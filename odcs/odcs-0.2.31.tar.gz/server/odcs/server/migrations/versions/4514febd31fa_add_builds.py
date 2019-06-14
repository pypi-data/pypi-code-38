"""Add Compose.builds.

Revision ID: 4514febd31fa
Revises: d1da07e15c54
Create Date: 2018-10-25 13:28:01.798873

"""

# revision identifiers, used by Alembic.
revision = '4514febd31fa'
down_revision = 'd1da07e15c54'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('composes', sa.Column('builds', sa.String(), nullable=True))


def downgrade():
    op.drop_column('composes', 'builds')
