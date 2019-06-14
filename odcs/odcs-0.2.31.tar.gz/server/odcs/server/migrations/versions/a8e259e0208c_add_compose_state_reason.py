"""Add Compose.state_reason

Revision ID: a8e259e0208c
Revises: e2163db7b15d
Create Date: 2018-01-10 15:27:18.492001

"""

# revision identifiers, used by Alembic.
revision = 'a8e259e0208c'
down_revision = 'e2163db7b15d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('composes', sa.Column('state_reason', sa.String(), nullable=True))


def downgrade():
    op.drop_column('composes', 'state_reason')
