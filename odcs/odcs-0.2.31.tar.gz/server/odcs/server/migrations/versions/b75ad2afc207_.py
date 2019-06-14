"""Add sigkeys field.

Revision ID: b75ad2afc207
Revises: c370b90de998
Create Date: 2017-10-03 13:41:42.303962

"""

# revision identifiers, used by Alembic.
revision = 'b75ad2afc207'
down_revision = 'c370b90de998'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('composes', sa.Column('sigkeys', sa.String(), nullable=True))


def downgrade():
    op.drop_column('composes', 'sigkeys')
