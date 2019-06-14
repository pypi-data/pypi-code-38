"""Add arches field to composes

Revision ID: 11b350234051
Revises: a8e259e0208c
Create Date: 2018-02-14 07:33:29.739034

"""

# revision identifiers, used by Alembic.
revision = '11b350234051'
down_revision = 'a8e259e0208c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('composes', sa.Column('arches', sa.String(), nullable=True, default="x86_64"))


def downgrade():
    op.drop_column('composes', 'arches')
