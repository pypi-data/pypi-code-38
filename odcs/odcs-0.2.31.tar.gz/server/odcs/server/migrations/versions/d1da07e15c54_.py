"""Add multilib_arches and multilib_method

Revision ID: d1da07e15c54
Revises: f4bc999818d7
Create Date: 2018-09-03 14:06:40.565612

"""

# revision identifiers, used by Alembic.
revision = 'd1da07e15c54'
down_revision = 'f4bc999818d7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('composes', sa.Column('multilib_arches', sa.String(), nullable=True,
                                        default=""))
    op.add_column('composes', sa.Column('multilib_method', sa.Integer(), nullable=True,
                                        default=0))


def downgrade():
    op.drop_column('composes', 'multilib_method')
    op.drop_column('composes', 'multilib_arches')
