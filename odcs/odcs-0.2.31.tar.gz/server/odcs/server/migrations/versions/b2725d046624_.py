"""add lookaside_repos column

Revision ID: b2725d046624
Revises: 4514febd31fa
Create Date: 2019-01-26 09:17:33.392547

"""

# revision identifiers, used by Alembic.
revision = 'b2725d046624'
down_revision = '4514febd31fa'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('composes', sa.Column('lookaside_repos', sa.String(), nullable=True))


def downgrade():
    op.drop_column('composes', 'lookaside_repos')
